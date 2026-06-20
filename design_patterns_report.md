# Báo cáo Phân tích Design Pattern: Composite & Command

Báo cáo này phân tích chi tiết hai mẫu thiết kế (Design Pattern) **Composite** và **Command** được triển khai trong mã nguồn của ứng dụng đặt tour du lịch và khách sạn (**Booking Travel**). 

---

## 1. MẪU THIẾT KẾ COMPOSITE (COMPOSITE DESIGN PATTERN)

### 1.1. Khái niệm và Mục đích
**Composite Pattern** là một mẫu thiết kế cấu trúc (Structural Pattern) cho phép bạn nhóm các đối tượng có quan hệ tương tự nhau thành một cấu trúc cây (tree structure). Mẫu thiết kế này cho phép các client (đối tượng sử dụng cấu trúc này) tương tác với các đối tượng đơn lẻ (Leaf) và các nhóm đối tượng (Composite) một cách hoàn toàn đồng nhất.

**Mục đích trong dự án:**
Trong hệ thống Booking Travel, Composite Pattern được sử dụng ở 3 module chính:
1. **Quản lý Giỏ hàng/Combo Booking (`AbstractBookingItem`):** Tính tổng giá tiền (`total_price`) cho các combo bao gồm các dịch vụ Tour (tính theo số người lớn/trẻ em) một cách đồng bộ.
2. **Quản lý Cấu hình hệ thống (`AbstractSettingNode`):** Nhóm các cài đặt đơn lẻ thành các danh mục cài đặt (API Settings, SMTP Settings, General Settings...) và xuất dữ liệu ra định dạng JSON phẳng hoặc phân cấp.
3. **Quản lý Nhóm Tour (`AbstractTourNode`):** Tổ chức hiển thị danh sách Tour theo Nhóm địa điểm, Nhóm tác giả hoặc Trạng thái.

### 1.2. Sơ đồ lớp UML (UML Class Diagram) - Booking Composite
Dưới đây là sơ đồ UML dạng nét đứt (ASCII Art) mô tả cách triển khai Composite Pattern cho tính năng quản lý Combo Booking:

```text
                      +-----------------------------+
                      |    AbstractBookingItem      | <-----------------------.
                      +-----------------------------+                         |
                      | + get_total_price() : float |                         |
                      | + show_details(indent) : str|                         |
                      | + to_dict() : dict          |                         |
                      +-----------------------------+                         |
                                     ^                                        |
                                     . (implements)                           |
                                     |                                        |
                      +------------------------------+                        |
                      |       TourBookingItem        |                        |
                      +------------------------------+                        |
                      | - tour : Tour                |                        |
                      | - persons : int              |                        |
                      +------------------------------+                        |
                      | + get_total_price() : float  |                        |
                      | + show_details(indent) : str |                        |
                      | + to_dict() : dict           |                        |
                      +------------------------------+                        |
                                                                              |
  +---------------------------------------------------------------------+     |
  |                            BookingPackage                           | ----. (contains list of)
  +---------------------------------------------------------------------+
  | - package_name : str                                                |
  | - items : List[AbstractBookingItem]                                 |
  +---------------------------------------------------------------------+
  | + add_item(item : AbstractBookingItem) : void                       |
  | + remove_item(item : AbstractBookingItem) : void                    |
  | + get_total_price() : float                                         |
  | + show_details(indent : str) : str                                  |
  | + to_dict() : dict                                                  |
  +---------------------------------------------------------------------+
```

### 1.3. Giải thích chi tiết các thành phần trong code
Dựa vào các tệp tin trong thư mục [composite](file:///d:/python/booking_travel/src/composite):

1. **Component (`AbstractBookingItem`):** 
   - Định nghĩa trong [abstract_booking.py](file:///d:/python/booking_travel/src/composite/abstract_booking.py).
   - Là một lớp trừu tượng (Interface/Abstract Class) khai báo các phương thức chung: `get_total_price()`, `show_details()`, và `to_dict()`.
2. **Leaf (`TourBookingItem`):**
   - Định nghĩa trong [tour.py](file:///d:/python/booking_travel/src/composite/tour.py).
   - Đại diện cho dịch vụ Tour du lịch. Công thức tính giá: `(giá người lớn * số người) + (giá trẻ em * số người)`.
3. **Composite (`BookingPackage`):**
   - Định nghĩa trong [booking.py](file:///d:/python/booking_travel/src/composite/booking.py).
   - Đại diện cho một "gói combo" chứa danh sách nhiều `AbstractBookingItem` bên trong (có thể là các tour lẻ lồng nhau).
   - Triển khai phương thức tính giá tổng:
     ```python
     def get_total_price(self) -> float:
         return sum(item.get_total_price() for item in self.items)
     ```
   - Cho phép thêm/bớt các phần tử con bằng các phương thức `add_item(item)` và `remove_item(item)`.

### 1.4. Ví dụ ứng dụng thực tế trong Service
Trong tệp tin [booking_service.py](file:///d:/python/booking_travel/src/service/booking_service.py#L24-L32), khi khách hàng chọn mua một combo du lịch gồm tour, hệ thống thực hiện gom các item này vào một `BookingPackage`:
```python
# Tạo gói combo chứa nhiều dịch vụ con
combo = BookingPackage(package_name=f"Combo Du lịch của User {user_id}")
if tour:
    combo.add_item(TourBookingItem(tour, persons))

# Tính tổng giá tiền cực kỳ dễ dàng
total_price = combo.get_total_price()
print(combo.show_details())
```

### 1.5. Cấu trúc phân cấp Tour (TourNode Composite)
Bên cạnh quản lý giỏ hàng, ứng dụng còn sử dụng một phân cấp Composite khác để tổ chức và phân loại các Tour du lịch phục vụ việc hiển thị sơ đồ cây hoặc báo cáo thống kê theo các tiêu chí: **Địa điểm (Location) -> Danh mục (Category) -> Tour lẻ (Leaf)**.

#### Sơ đồ lớp UML (UML Class Diagram) - Tour Composite
Dưới đây là sơ đồ UML dạng nét đứt (ASCII Art) mô tả cấu trúc phân cấp Tour:

```text
                      +-----------------------------+
                      |      AbstractTourNode       | <-----------------------.
                      +-----------------------------+                         |
                      | + get_tour_count() : int    |                         |
                      | + show_tours(indent) : str  |                         |
                      | + to_dict() : dict          |                         |
                      +-----------------------------+                         |
                                     ^                                        |
                                     . (implements)                           |
                 .-------------------o-------------------.                    |
                 .                                       .                    |
  +------------------------------+       +------------------------------+     |
  |         TourLeafNode         |       |      TourGroupComposite      | ----. (contains list of)
  +------------------------------+       +------------------------------+
  | - tour : Tour                |       | - group_name : str           |
  +------------------------------+       | - group_type : str           |
  | + get_tour_count() : int     |       | - children : List            |
  | + show_tours(indent) : str   |       +------------------------------+
  | + to_dict() : dict           |       | + add_child(comp) : void     |
  +------------------------------+       | + remove_child(comp) : void  |
                                         | + get_tour_count() : int     |
                                         | + show_tours(indent) : str   |
                                         | + to_dict() : dict           |
                                         +------------------------------+
```

#### Giải thích các thành phần:
1. **Component (`AbstractTourNode`):**
   - Khai báo trong [abstract_tour.py](file:///d:/python/booking_travel/src/composite/abstract_tour.py).
   - Quy định các phương thức chung cho cả node đơn lẻ và nhóm node: tính tổng số tour (`get_tour_count`), in dạng cây (`show_tours`) và chuyển dữ liệu sang dict (`to_dict`).
2. **Leaf (`TourLeafNode`):**
   - Khai báo trong [tour.py](file:///d:/python/booking_travel/src/composite/tour.py).
   - Đại diện cho 1 Tour đơn lẻ. Có `get_tour_count()` luôn trả về `1` và hiển thị trạng thái duyệt của Tour đó (`DRAFT` / `PENDING` / `PUBLISHED`).
3. **Composite (`TourGroupComposite`):**
   - Khai báo trong [tour.py](file:///d:/python/booking_travel/src/composite/tour.py).
   - Đại diện cho một nhóm tour (VD: Nhóm Hà Nội, Nhóm Đà Nẵng) hoặc nhóm danh mục (Nghỉ dưỡng, Mạo hiểm).
   - Chứa danh sách các node con `children` và tự động tính tổng số tour của nhóm bằng cách cộng đồn đệ quy từ các con:
     ```python
     def get_tour_count(self) -> int:
         return sum(child.get_tour_count() for child in self.children)
     ```

#### Ví dụ ứng dụng thực tế trong Service
Trong [tour_client_service.py](file:///d:/python/booking_travel/src/service/tour_client_service.py#L161-L215), hệ thống xây dựng cây phân cấp tự động bằng cách lồng các `TourGroupComposite` vào nhau:
```python
# Gốc cây lớn
root = TourGroupComposite("Tất cả điểm đến", "Hệ thống")

# Khởi tạo các nhóm theo địa điểm
for loc in locations:
    group = TourGroupComposite(loc.city, "Địa điểm")
    root.add_child(group)

# Đưa các tour vào đúng địa điểm và danh mục của chúng
for tour in tours:
    loc_group = location_groups.get(tour.location_id, unknown_location_group)
    
    # Tìm hoặc tạo danh mục (Category) bên trong địa điểm đó
    category_group = None
    category_name = tour.category_name or "Khác"
    for child in loc_group.children:
        if isinstance(child, TourGroupComposite) and child.group_name == category_name:
            category_group = child
            break
            
    if not category_group:
        category_group = TourGroupComposite(category_name, "Danh mục")
        loc_group.add_child(category_group)
        
    # Thêm tour đơn lẻ làm Leaf Node
    category_group.add_child(TourLeafNode(tour))
```

---

## 2. MẪU THIẾT KẾ COMMAND (COMMAND DESIGN PATTERN)

### 2.1. Khái niệm và Mục đích
**Command Pattern** là một mẫu thiết kế hành vi (Behavioral Pattern) giúp chuyển đổi một yêu cầu (request) thành một đối tượng độc lập chứa tất cả thông tin về yêu cầu đó. Việc đóng gói này cho phép tham số hóa các client với các yêu cầu khác nhau, lưu giữ lịch sử thực thi để hỗ trợ **Undo/Redo**, và quản lý an toàn các giao dịch cơ sở dữ liệu (Transaction).

**Mục đích trong dự án:**
Trong hệ thống Booking Travel, các thao tác ghi dữ liệu xuống Database (thêm, sửa, xóa, duyệt tour, cập nhật cấu hình, đăng ký người dùng) đều được thực hiện qua Command Pattern. 
- **Đóng gói logic nghiệp vụ** thành các Command độc lập.
- **Hỗ trợ cơ chế Transaction Rollback & Undo:** Nếu một chuỗi các thao tác thay đổi dữ liệu bị lỗi ở bước bất kỳ, hệ thống sẽ thực hiện `session.rollback()` đối với database và gọi phương thức `undo()` trên từng Command đã chạy thành công trước đó để đồng bộ lại dữ liệu trong RAM/Database (ví dụ: chuyển từ trạng thái `PENDING` sang `CANCELLED` hoặc hủy bản ghi tạm).

### 2.2. Sơ đồ lớp UML (UML Class Diagram) - Database Command
Dưới đây là sơ đồ UML dạng nét đứt (ASCII Art) mô tả cơ chế thực thi và đảo ngược giao dịch cơ sở dữ liệu bằng Command Pattern:

```text
                     +-----------------------------+
                     |       DatabaseCommand       | <-------------------------------------------.
                     +-----------------------------+                                             |
                     | + execute(session) : void   |                                             |
                     | + undo(session) : void      |                                             |
                     +-----------------------------+                                             |
                                    ^                                                            |
                                    . (implements)                                               |
          .-------------------------o-------------------------.                                  |
          .                         .                         .                                  |
+---------------------+   +---------------------+   +---------------------+                      |
| CreateBookingCommand|   |ProcessPaymentCommand|   |ToggleUserStatusCommand|                    |
+---------------------+   +---------------------+   +---------------------+                      |
| - data : dict       |   | - booking_cmd : ... |   | - user_id : int     |                      |
| - record : Bookings |   | - amount : float    |   | - record : User     |                      |
+---------------------+   +---------------------+   +---------------------+                      |
| + execute() : void  |   | + execute() : void  |   | + execute() : void  |                      |
| + undo() : void     |   | + undo() : void     |   | + undo() : void     |                      |
+---------------------+   +---------------------+   +---------------------+                      |
                                                                                                 |
                     +----------------------------------------------------+                      |
                     |                DBTransactionInvoker                | ---------------------. (executes & stores)
                     +----------------------------------------------------+
                     | - history : List[DatabaseCommand]                  |
                     +----------------------------------------------------+
                     | + execute_transaction(session, commands) : void    |
                     +----------------------------------------------------+
```

### 2.3. Giải thích chi tiết các thành phần trong code
Dựa vào các tệp tin trong thư mục [command](file:///d:/python/booking_travel/src/command):

1. **Interface Command (`DatabaseCommand`):**
   - Khai báo trong [component.py](file:///d:/python/booking_travel/src/command/component.py).
   - Định nghĩa hai phương thức trừu tượng `execute(session)` (thực thi tác vụ ghi database) và `undo(session)` (khôi phục trạng thái cũ).
2. **Concrete Commands (Các lớp lệnh cụ thể):**
   - `CreateBookingCommand`: Khởi tạo bản ghi Booking ở trạng thái `PENDING`. Nếu `undo()` được gọi, nó chuyển trạng thái sang `CANCELLED`.
   - `ProcessPaymentCommand`: Tạo bản ghi thanh toán. Nếu `undo()`, chuyển trạng thái thanh toán sang `REFUNDED`.
   - `CreateTourCommand`: Thêm mới Tour. Nếu `undo()`, xóa bản ghi tour khỏi database (`session.delete`).
   - `ToggleUserStatusCommand`: Đảo ngược trạng thái hoạt động (`is_active`) của người dùng.
3. **Invoker (`DBTransactionInvoker`):**
   - Đóng vai trò thực thi chuỗi lệnh và quản lý Transaction.
   - Khi chạy `execute_transaction`, nó lưu các lệnh đã chạy thành công vào danh sách lịch sử `_history`. Nếu xảy ra ngoại lệ ở bất kỳ lệnh nào:
     1. Thực hiện `session.rollback()` để xóa các lệnh đã lưu tạm trên database.
     2. Lần lượt duyệt ngược danh sách `_history` để gọi hàm `undo()` trên từng Command nhằm khôi phục trạng thái bộ nhớ/bản ghi.
     ```python
     # Logic xử lý rollback trong DBTransactionInvoker
     def execute_transaction(self, session, commands: list[DatabaseCommand]):
         try:
             for command in commands:
                 command.execute(session)
                 self._history.append(command)
             session.commit()
             self._history.clear()
         except Exception as e:
             session.rollback()
             for command in reversed(self._history):
                 command.undo(session)
             raise e
     ```
4. **Receiver:**
   - Chính là cơ sở dữ liệu được truy cập thông qua đối tượng `SQLAlchemy Session` và các lớp Model của SQLAlchemy (`User`, `Tour`, `Bookings`, `Payment`).

---

## 3. SỰ KẾT HỢP GIỮA COMPOSITE VÀ COMMAND PATTERN

Trong dự án này, sự kết hợp giữa hai mẫu thiết kế được thể hiện rõ nét nhất ở quy trình **đặt một gói dịch vụ du lịch (Combo Booking)**:

1. **Bước 1 (Composite):** Client gom các thông tin dịch vụ đơn lẻ (Tour) của người dùng thành một đối tượng phức hợp `BookingPackage`. Phương thức `combo.get_total_price()` được gọi để tự động tính tổng tiền của cả gói mà không cần quan tâm chi tiết cách tính giá của từng thành phần con.
2. **Bước 2 (Command):** Một tập hợp các lệnh bao gồm `CreateBookingCommand` và `ProcessPaymentCommand` được gửi tới `DBTransactionInvoker`.
3. **Bước 3 (Thực thi an toàn):** Invoker thực thi các lệnh. Nếu tạo booking thành công nhưng bước xử lý thanh toán bị lỗi (ví dụ: lỗi cổng thanh toán, thiếu số dư), cơ chế `undo()` và `session.rollback()` sẽ lập tức được kích hoạt để chuyển trạng thái Booking thành `CANCELLED` và khôi phục trạng thái cơ sở dữ liệu về ban đầu, đảm bảo tính toàn vẹn dữ liệu cực kỳ chặt chẽ.

---

## 4. ĐÁNH GIÁ (ƯU VÀ NHƯỢC ĐIỂM) ĐỂ VIẾT BÁO CÁO TIỂU LUẬN

### 4.1. Đối với Composite Pattern
* **Ưu điểm:**
  - **Dễ dàng quản lý cấu trúc cây:** Giúp code biểu diễn các thực thể lồng nhau (Combo gồm nhiều Tour, Thư mục cài đặt gồm các khóa cấu hình con) một cách rõ ràng.
  - **Tính đa hình cao:** Client không cần viết các câu lệnh điều kiện `if-else` phức tạp để phân biệt xem mình đang xử lý một Tour đơn lẻ hay một gói dịch vụ tổng hợp. Chỉ cần gọi phương thức chung.
  - **Dễ mở rộng:** Việc thêm các loại dịch vụ mới (vé máy bay, thuê xe) chỉ yêu cầu tạo một lớp Leaf mới kế thừa `AbstractBookingItem` mà không cần sửa đổi mã nguồn hiện có (tuân thủ nguyên lý Open/Closed).
* **Nhược điểm:**
  - **Khó giới hạn thành phần:** Đôi khi việc thiết kế một interface quá chung cho cả Leaf và Composite khiến một số phương thức không thực sự hợp lý với Leaf (ví dụ: Leaf vẫn phải kế thừa hoặc chịu ảnh hưởng bởi các hành vi quản lý con của Composite nếu thiết kế interface không khéo).

### 4.2. Đối với Command Pattern
* **Ưu điểm:**
  - **Tách biệt mối quan tâm (Decoupling):** Lớp gọi yêu cầu (Invoker/Controller) hoàn toàn không biết chi tiết cách thức một Tour được tạo hay cách thức trạng thái thanh toán được cập nhật (Receiver).
  - **Hỗ trợ Undo/Redo và Transaction xuất sắc:** Việc quản lý lịch sử các lệnh chạy trong RAM cho phép viết logic đảo ngược tác vụ lỗi vô cùng dễ dàng và an toàn.
  - **Thiết kế dạng lắp ghép (Composition):** Dễ dàng gom nhiều lệnh đơn lẻ thành một chuỗi giao dịch phức tạp (Macro Command) để thực thi tuần tự.
* **Nhược điểm:**
  - **Tăng số lượng lớp (Class proliferation):** Mỗi thao tác nghiệp vụ nhỏ (Tạo tour, duyệt tour, khóa user...) đều yêu cầu tạo một class Command mới, làm phình to cấu trúc thư mục code.
  - **Độ phức tạp tăng:** Đòi hỏi lập trình viên phải thiết kế logic `undo()` cẩn thận và đồng bộ hóa tốt với trạng thái của Transaction database.
