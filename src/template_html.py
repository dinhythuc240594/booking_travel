
EMAIL_BODY_HTML = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                            max-width: 600px;
                            margin: 0 auto;
                            padding: 20px;
                        }}
                        .header {{
                            background-color: #dc3545;
                            color: white;
                            padding: 20px;
                            text-align: center;
                            border-radius: 5px 5px 0 0;
                        }}
                        .content {{
                            background-color: #f8f9fa;
                            padding: 20px;
                            border: 1px solid #dee2e6;
                        }}
                        .reason-box {{
                            background-color: white;
                            border-left: 4px solid #dc3545;
                            padding: 15px;
                            margin: 20px 0;
                        }}
                        .tour-link {{
                            display: inline-block;
                            background-color: #0066cc;
                            color: white;
                            padding: 12px 24px;
                            text-decoration: none;
                            border-radius: 5px;
                            margin: 20px 0;
                        }}
                        .footer {{
                            text-align: center;
                            color: #6c757d;
                            font-size: 12px;
                            margin-top: 20px;
                            padding-top: 20px;
                            border-top: 1px solid #dee2e6;
                        }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h2>Thông báo từ chối bài viết</h2>
                    </div>
                    <div class="content">
                        <p>Xin chào <strong>{0}</strong>,</p>
                        
                        <p>Chúng tôi rất tiếc phải thông báo rằng tour của bạn đã bị từ chối:</p>
                        
                        <h3 style="color: #0066cc;">{1}</h3>
                        
                        <div class="reason-box">
                            <strong>Lý do từ chối:</strong>
                            <p style="margin-top: 10px; white-space: pre-wrap;">{2}</p>
                        </div>
                        
                        <p>Bạn có thể xem lại tour của mình tại link sau:</p>
                        <div style="text-align: center;">
                            <a href="{3}" class="tour-link">Xem tour</a>
                        </div>
                        
                        <p>Vui lòng xem xét lại tour và chỉnh sửa theo góp ý trên trước khi gửi lại để duyệt.</p>
                        
                        <p>Trân trọng,<br>
                        <strong>Ban biên tập BookingTravel</strong></p>
                    </div>
                    <div class="footer">
                        <p>Đây là email tự động. Vui lòng không trả lời email này.</p>
                        <p>© 2024 BookingTravel. All rights reserved.</p>
                    </div>
                </body>
                </html>
"""

EMAIL_SUBJECT_TEST = "Test Email - BookingTravel"
EMAIL_BODY_HTML_TEST = """
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2c3e50;">Email Test thành công!</h2>
                    <p>Đây là email test từ hệ thống BookingTravel.</p>
                    <p>Nếu bạn nhận được email này, có nghĩa là cài đặt SMTP của bạn đã hoạt động đúng.</p>
                    <p style="color: #7f8c8d; font-size: 12px; margin-top: 30px;">
                        Đây là email tự động. Vui lòng không trả lời email này.
                    </p>
                </div>
            </body>
            </html>
            """
EMAIL_BODY_TEXT_TEST = """Email Test thành công!

Đây là email test từ hệ thống BookingTravel.

Nếu bạn nhận được email này, có nghĩa là cài đặt SMTP của bạn đã hoạt động đúng.
"""

