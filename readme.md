https://www.hanoigoclub.com/2018/09/nen-tang-va-luat-co-vay.html
# Go Game - Luật chơi và Hướng dẫn

## 1. Tổng quan
- Go là trò chơi cờ chiến thuật 2 người: Đen và Trắng.
- Bàn cờ mặc định là 19*19 (có thể thay đổi trong file `config.py`).
- Mục tiêu: Vây đất (các ô trống) và bắt quân của đối thủ để có điểm cao hơn.

## 2. Luật chơi cơ bản

### 2.1. Đặt quân
- Người chơi luân phiên đặt quân (Đen đi trước):
  - Đen là số 1, Trắng là số 2.
  - Đặt quân vào các ô trống (ô có giá trị 0).
- Không được đặt quân ở ô đã có quân, hoặc nếu nước đi vi phạm luật Ko (xem bên dưới).

### 2.2. Bắt quân
- Một nhóm quân (các quân cùng màu nối với nhau) bị bắt nếu không còn **khí**:
  - Khí là các ô trống liền kề nhóm (lên, xuống, trái, phải).
  - Nếu nhóm không còn khí, nó bị xóa khỏi bàn cờ và được tính là **tù binh** của đối thủ.
- Khi đặt quân, nếu làm nhóm của đối thủ hết khí, nhóm đó bị bắt ngay lập tức.
- Không được đặt quân ở vị trí tự sát (làm nhóm của mình hết khí), trừ khi nước đi đó bắt được quân đối thủ.

### 2.3. Luật Ko
- Không được đặt quân nếu nước đi lặp lại trạng thái bàn cờ trước đó (gọi là luật Ko).
- Ví dụ: Nếu bạn vừa bắt 1 quân của đối thủ, đối thủ không thể đặt lại ngay để bắt lại quân của bạn, vì bàn cờ sẽ lặp lại trạng thái cũ.

### 2.4. Pass lượt
- Người chơi có thể pass lượt (bỏ qua lượt của mình).
- Nếu cả hai người chơi pass liên tiếp, game kết thúc.

### 2.5. Kết thúc game và tính điểm
- Game kết thúc khi cả hai người chơi pass liên tiếp.
- Khi game kết thúc, các nhóm quân **chết** sẽ bị xóa:
  - Một nhóm chết nếu không có **mắt** (eye) và không thể tạo được 2 mắt.
  - Mắt là một ô trống (hoặc nhóm ô trống) được vây hoàn toàn bởi quân của bạn.
  - Nhóm sống nếu:
    - Có ít nhất 2 mắt.
    - Hoặc có vùng trống được vây hoàn toàn bởi nhóm, với ít nhất 4 ô (đủ để tạo 2 mắt).
- **Tính điểm** (theo luật Nhật Bản):
  - Điểm = Số tù binh + Số ô đất (ô trống được vây hoàn toàn bởi quân của bạn).
  - Trắng được cộng thêm **Komi** (mặc định 6.5 điểm, để bù cho việc Đen đi trước).
- Người có điểm cao hơn thắng.

## 3. Các tính năng trong game
- **Đặt quân**: Đặt quân tại vị trí (row, col) bằng hàm `place_stone(row, col)`.
- **Pass lượt**: Pass lượt bằng hàm `pass_turn()`. Nếu cả hai pass liên tiếp, game kết thúc và tính điểm.
- **Hoàn tác (Undo)**: Quay lại nước đi trước bằng hàm `undo()`. Chỉ hoạt động nếu game chưa kết thúc.
- **Reset**: Đặt lại bàn cờ về trạng thái ban đầu bằng hàm `reset()`.
- **Tính điểm**: Dùng hàm `calculate_score()` để lấy điểm của Đen và Trắng.
- **Xem người thắng**: Dùng hàm `get_winner()` để xem ai thắng (chỉ có kết quả khi game kết thúc).

## 4. Cách chơi (dùng giao diện Pygame)
- Chạy file `go_game.py` để mở giao diện.
- **Đặt quân**: Click chuột vào ô trên bàn cờ.
- **Pass lượt**: Nhấn phím `P`.
- **Hoàn tác**: Nhấn phím `U`.
- **Reset**: Nhấn phím `R`.
- **Thoát**: Đóng cửa sổ hoặc nhấn `Escape`.

## 5. Cách giả lập (không cần giao diện)
- Dùng file `simulate_game.py` để chạy giả lập:
  - Đặt quân, pass, undo, reset từng bước.
  - Hiển thị UI sau mỗi bước, nhấn `Space` hoặc `Enter` để tiếp tục.

## 6. Lưu ý
- Game hiện tại chưa xử lý luật **Tam kiếp** (superko), chỉ có luật Ko cơ bản.
- Một số trường hợp nhóm sống/chết có thể không chính xác 100% (vì logic kiểm tra mắt còn đơn giản).

## 7. Cấu trúc code
- `board.py`: Chứa logic chính của bàn cờ (đặt quân, tính điểm, kiểm tra nhóm sống/chết).
- `game_controller.py`: Giao diện để điều khiển game (đặt quân, pass, undo, v.v.).
- `go_game.py`: Chứa giao diện Pygame và vòng lặp chính.
- `simulate_game.py`: Giả lập chạy từng bước với UI.
- `config.py`: Cấu hình (kích thước bàn cờ, Komi, v.v.).
- `render.py`: Vẽ giao diện Pygame.
