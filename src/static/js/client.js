
UI_CLIENT = {

    SITE: 'vn',

    homeMainContent: async function(){
        UI_CLIENT.updateDateTime();
        await UI_CLIENT.loadDynamicMenu();
    },

    updateDateTime: function() {
        var now = new Date();
        var options = {
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };

        options.locale = UI_CLIENT.SITE == 'vn'? 'vi-VN':'en-US';
        setInterval(function(){
            var dateTimeString = now.toLocaleDateString(options.locale, options);
            $('#current-date-time').text(dateTimeString);
        }, 60000);
    },

    formatTimeAgoFromIso: async function(dateStr) {
        if (!dateStr) return MyLang.getMsg('JUST_NOW');
        const date = new Date(dateStr);
        const now = new Date();
        const diffMs = now - date;
        const diffMinutes = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMinutes / 60);
        const diffDays = Math.floor(diffHours / 24);

        if (diffDays > 0) return diffDays + MyLang.getMsg('DAY_AGO');
        if (diffHours > 0) return diffHours + MyLang.getMsg('HOUR_AGO');
        if (diffMinutes > 0) return diffMinutes + MyLang.getMsg('MINUTE_AGO');
        return MyLang.getMsg('JUST_NOW');
    },

    validateEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    loadWeatherData: async function(){
        var weatherWidget = $('#weather-widget');
        if (!weatherWidget.length) return;
        fetch(`https://geocoding-api.open-meteo.com/v1/search?name=Saigon&count=1&language=${UI_CLIENT.SITE}&format=json`)
            .then(response => response.json())
            .then(data => {
                if (data.results && data.results.length > 0) {
                    const location = data.results[0];
                    const latitude = location.latitude;
                    const longitude = location.longitude;
                    const cityName = 'TP. Hồ Chí Minh';
                    
                    // Get current weather
                    return fetch(`https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&timezone=Asia/Ho_Chi_Minh`)
                        .then(response => response.json())
                        .then(weatherData => {
                            displayWeather(cityName, weatherData);
                        });
                } else {
                    throw new Error('Không tìm thấy thành phố');
                }
            })
            .catch(error => {
                console.error('Weather API error:', error);
                // Fallback to wttr.in API
                loadWeatherFallback(city);
            });
    },

    loadWeatherFallback: async function(city){
        fetch(`https://wttr.in/${city}?format=j1&lang=vi`)
            .then(response => response.json())
            .then(data => {
                if (data.current_condition && data.current_condition[0]) {
                    const current = data.current_condition[0];
                    const location = data.nearest_area[0].areaName[0].value;
                    
                    const weatherData = {
                        current: {
                            temperature_2m: parseFloat(current.temp_C),
                            relative_humidity_2m: parseFloat(current.humidity),
                            wind_speed_10m: parseFloat(current.windspeedKmph) / 3.6, // Convert km/h to m/s
                            weather_code: getWeatherCode(current.weatherDesc[0].value)
                        }
                    };
                    
                    displayWeather(location, weatherData);
                } else {
                    throw new Error('Không thể lấy dữ liệu thời tiết');
                }
            })
            .catch(error => {
                console.error('Weather fallback error:', error);
                displayWeatherError();
            });
    },

    displayWeather: function name(cityName, weatherData) {
        const weatherWidget = $('#weather-widget');
        const current = weatherData.current;
        
        // Get weather icon and description
        const weatherInfo = getWeatherInfo(current.weather_code);
        const time = new Date(current.time);
        const hours = time.getHours();
        // const minutes = time.getMinutes();
        // const seconds = time.getSeconds();
        // const timeString = `${hours}:${minutes}:${seconds}`;

        if((hours > 6 && hours < 18) && (weatherInfo.icon == 'fas fa-sun' || weatherInfo.icon == 'fas fa-cloud-sun')) {
            weatherInfo.icon = 'fas fa-sun';
            weatherInfo.description = MyLang.getMsg('MSG_SUN');
        } else {
            if((hours > 18 && hours < 24) || (hours > 0 && hours < 6)) {
                weatherInfo.icon = 'fas fa-moon';
                weatherInfo.description = MyLang.getMsg('MSG_NIGHT');
            }
        }
        
        const temperature = Math.round(current.temperature_2m);
        const humidity = Math.round(current.relative_humidity_2m);
        const windSpeed = Math.round(current.wind_speed_10m * 3.6); // Convert m/s to km/h
        
        var html = '';
            html += '<div class="city-name">'+ cityName +'</div>';
            html += '<div class="temperature">'+ temperature + MyLang.getMsg('MSG_OPERATOR_TEMP') + '</div>';
            html += '<div class="weather-desc">';
            html += '<i class="'+ weatherInfo.icon +'"></i>' + weatherInfo.description;
            html += '</div>';
            html += '<div class="weather-details">';
            html += '<div class="detail-item">';
            html += '<i class="fas fa-tint"></i>';
            html += '<span>'+ MyLang.getMsg('MSG_HUMIDITY') + humidity +'%</span>';
            html += '</div>';
            html += '<div class="detail-item">';
            html += '<i class="fas fa-wind"></i>';
            html += '<span>'+ MyLang.getMsg('MSG_WINDY') + windSpeed +'km/h</span>';
            html += '</div>';
            html += '</div>';
        
        weatherWidget.html(weatherHTML);
    },

    // Get weather icon and description from weather code (WMO Weather interpretation codes)
    getWeatherInfo: function(code) {
        const weatherMap = {
            0: { icon: 'fas fa-sun', description: MyLang.getMsg('MSG_SUN') },
            1: { icon: 'fas fa-sun', description: MyLang.getMsg('MSG_CLEAR_SKY') },
            2: { icon: 'fas fa-cloud-sun', description: MyLang.getMsg('MSG_FEW_CLOUDY') },
            3: { icon: 'fas fa-cloud', description: MyLang.getMsg('MSG_MANY_CLOUDY') },
            45: { icon: 'fas fa-smog', description: MyLang.getMsg('MSG_FOG') },
            48: { icon: 'fas fa-smog', description: MyLang.getMsg('MSG_FOG') },
            51: { icon: 'fas fa-cloud-rain', description: MyLang.getMsg('MSG_LIGHT_RAIN') },
            53: { icon: 'fas fa-cloud-rain', description: MyLang.getMsg('MSG_MODERATE_RAIN') },
            55: { icon: 'fas fa-cloud-rain', description: MyLang.getMsg('MSG_HEAVY_RAIN') },
            56: { icon: 'fas fa-cloud-rain', description: MyLang.getMsg('MSG_LIGHT_HAIL') },
            57: { icon: 'fas fa-cloud-rain', description: MyLang.getMsg('MSG_HEAVY_HAIL') },
            61: { icon: 'fas fa-cloud-showers-heavy', description: MyLang.getMsg('MSG_LIGHT_RAIN') },
            63: { icon: 'fas fa-cloud-showers-heavy', description: MyLang.getMsg('MSG_MODERATE_RAIN') },
            65: { icon: 'fas fa-cloud-showers-heavy', description: MyLang.getMsg('MSG_HEAVY_RAIN') },
            66: { icon: 'fas fa-cloud-rain', description: MyLang.getMsg('MSG_LIGHT_HAIL') },
            67: { icon: 'fas fa-cloud-rain', description: MyLang.getMsg('MSG_HEAVY_HAIL') },
            71: { icon: 'fas fa-snowflake', description: MyLang.getMsg('MSG_LIGHT_SNOW') },
            73: { icon: 'fas fa-snowflake', description: MyLang.getMsg('MSG_MODERATE_SNOW') },
            75: { icon: 'fas fa-snowflake', description: MyLang.getMsg('MSG_HEAVY_SNOW') },
            77: { icon: 'fas fa-snowflake', description: MyLang.getMsg('MSG_SNOW_FLAKES') },
            80: { icon: 'fas fa-cloud-showers-heavy', description: MyLang.getMsg('MSG_LIGHT_SHOWER') },
            81: { icon: 'fas fa-cloud-showers-heavy', description: MyLang.getMsg('MSG_MODERATE_SHOWER') },
            82: { icon: 'fas fa-cloud-showers-heavy', description: MyLang.getMsg('MSG_HEAVY_SHOWER') },
            85: { icon: 'fas fa-snowflake', description: MyLang.getMsg('MSG_LIGHT_SNOW_FALL') },
            86: { icon: 'fas fa-snowflake', description: MyLang.getMsg('MSG_HEAVY_SNOW_FALL') },
            95: { icon: 'fas fa-bolt', description: MyLang.getMsg('MSG_THUNDER') },
            96: { icon: 'fas fa-bolt', description: MyLang.getMsg('MSG_THUNDER_HAIL') },
            99: { icon: 'fas fa-bolt', description: MyLang.getMsg('MSG_THUNDER_HEAVY_HAIL') },
        };
        
        return weatherMap[code] || { icon: 'fas fa-cloud', description: MyLang.getMsg('MSG_MANY_CLOUDY') };
    },

    loadDynamicMenu: async function(){
        const menuTree = await menuManager.buildMenuTree();
        console.log('Menu Tree:', menuTree);
        let menuHtml = '';
        
        menuTree.forEach(menu => {
            const hasChildren = menu.children && menu.children.length > 0;
            console.log(`Menu: ${menu.name}, Has Children: ${hasChildren}, Children:`, menu.children);
            
            const icon = menu.icon ? '<i class="'+ menu.icon +'"></i> ' : '';
            const activeClass = menu.order === 0 ? 'active' : '';
            const submenuClass = hasChildren ? 'has-submenu' : '';
            
            // Build class list properly
            const classList = [activeClass, submenuClass].filter(c => c).join(' ');
            
            menuHtml += '<li class="'+ classList +'" data-slug="'+ menu.slug +'">';
            menuHtml += '<a href="'+ menu.slug+'.html">'+ icon + menu.name +'</a>';
            
            if (hasChildren) {
                console.log(`Adding submenu for ${menu.name} with ${menu.children.length} children`);
                menuHtml += '<ul class="submenu">';
                menu.children.forEach(child => {
                    const childIcon = child.icon ? '<i class="'+ child.icon +'"></i> ' : '';
                    menuHtml += '<li data-slug="'+ child.slug +'">';
                    menuHtml += '<a href="#$'+child.slug+'">'+ childIcon + child.name +'</a>';
                    menuHtml += '</li>';
                });
                menuHtml += '</ul>';
            }
            
            menuHtml += '</li>';
        });
        
        // Add more menu button (will be shown/hidden by adjustMenuVisibility)
        menuHtml += '<li class="more-menu-btn">';
        menuHtml += '<a href="javascript:void(0)">';
        menuHtml += '<i class="fas fa-ellipsis-h"></i>'+ MyLang.getMsg('LOAD_MORE');
        menuHtml += '</a>';
        menuHtml += '<ul class="more-menu-dropdown"></ul>';
        menuHtml += '</li>';
        
        $('#mainMenu').html(menuHtml);
        
        console.log('Menu HTML loaded into #mainMenu');
        console.log('Elements with .has-submenu:', $('.has-submenu').length);
        console.log('Elements with .submenu:', $('.submenu').length);
        
        // Adjust menu visibility after load
        setTimeout(UI_CLIENT.adjustMenuVisibility, 100);
    },

    adjustMenuVisibility: function(){
        const navMenu = $('.nav-menu');
        const moreBtn = $('.more-menu-btn');
        const moreDropdown = $('.more-menu-dropdown');
        const menuItems = $('.nav-menu > li:not(.more-menu-btn)');
        
        if (!navMenu.length || !menuItems.length) return;
        
        // Reset
        menuItems.removeClass('nav-hidden');
        moreBtn.removeClass('show');
        moreDropdown.empty();
        
        const navWidth = navMenu.width();
        const moreBtnWidth = 120; // Width for "Xem thêm" button
        let totalWidth = 0;
        let hiddenMenus = [];
        
        menuItems.each(function(index) {
            const itemWidth = $(this).outerWidth(true);
            totalWidth += itemWidth;
            
            // Check if this item would overflow
            if (totalWidth > (navWidth - moreBtnWidth)) {
                $(this).addClass('nav-hidden');
                
                // Get menu data
                const menuSlug = $(this).data('slug');
                const menuHtml = $(this).clone();
                menuHtml.removeClass('nav-hidden active');
                
                // Build dropdown item
                let dropdownItem = '<li>';
                    dropdownItem += '<a href="#${menuSlug}">'+ menuHtml.find('> a').html() +'</a>';
                
                // Add submenu if exists
                const submenu = $(this).find('.submenu');
                if (submenu.length) {
                    dropdownItem += '<ul class="more-submenu">';
                    submenu.find('> li').each(function() {
                        const childSlug = $(this).data('slug');
                        const childName = $(this).find('a').text();
                        dropdownItem += '<li><a href="#'+ childSlug +'">'+ childName +'</a></li>';
                    });
                    dropdownItem += '</ul>';
                }
                
                dropdownItem += '</li>';
                hiddenMenus.push(dropdownItem);
            }
        });
        
        // Show more button if there are hidden menus
        if (hiddenMenus.length > 0) {
            moreDropdown.html(hiddenMenus.join(''));
            moreBtn.addClass('show');
        }
    }

};

TEMPLATE_CLIENT = {
    
    loadSectionFeatureNews: function(){
        
    }

};

