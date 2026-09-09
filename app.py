import cv2
import numpy as np

def main():
    # カメラの初期化（0番で開かない場合は 1 や 2 に変更）
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("エラー: Webカメラを開くことができませんでした。")
        return

    # ウインドウの作成と設定（リサイズ可能にする）
    cv2.namedWindow("Origami Step Assister", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Origami Step Assister", 960, 720)

    current_step = 1
    true_count = 0
    REQUIRED_TRUE_FRAMES = 30  # 判定安定化のために100から30に緩和

    print("プログラムを開始します。'q'キーで終了、'n'キーで手動ステップ進行。")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("エラー: フレームを取得できませんでした。")
            break

        # 描画用の複製を作成
        display = frame.copy()
        
        # 色空間変換
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # ----------------------------------------------------
        # 共通処理: 色マスクの作成 (青・黄)
        # ----------------------------------------------------
        lower_blue = np.array([90, 50, 50])
        upper_blue = np.array([130, 255, 255])
        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

        lower_yellow = np.array([15, 80, 80])
        upper_yellow = np.array([35, 255, 255])
        mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

        # 状態フラグ
        step_passed = False
        status_text = ""

        # ----------------------------------------------------
        # STEP 1
        # ----------------------------------------------------
        if current_step == 1:
            has_blue_triangle = False
            is_pentagon = False

            contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours_blue:
                largest = max(contours_blue, key=cv2.contourArea)
                if cv2.contourArea(largest) > 1000:
                    peri = cv2.arcLength(largest, True)
                    approx = cv2.approxPolyDP(largest, 0.04 * peri, True)
                    if len(approx) == 3:
                        has_blue_triangle = True
                        cv2.drawContours(display, [approx], -1, (255, 0, 0), 3)

            # 外形判定 (ガウシアンフィルタ + Otsu二値化)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            contours_outer, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours_outer:
                if cv2.contourArea(cnt) > 8000:
                    peri = cv2.arcLength(cnt, True)
                    approx = cv2.approxPolyDP(cnt, 0.03 * peri, True)
                    if 4 <= len(approx) <= 6:  # 4~6頂点を許容
                        is_pentagon = True
                        cv2.drawContours(display, [approx], -1, (0, 255, 0), 2)
                        break

            step_passed = has_blue_triangle and is_pentagon
            status_text = f"Blue Tri: {has_blue_triangle} | Pentagon: {is_pentagon}"

        # ----------------------------------------------------
        # STEP 2
        # ----------------------------------------------------
        elif current_step == 2:
            has_hexagon = False
            contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours_blue:
                largest = max(contours_blue, key=cv2.contourArea)
                if cv2.contourArea(largest) > 1000:
                    peri = cv2.arcLength(largest, True)
                    approx = cv2.approxPolyDP(largest, 0.03 * peri, True)
                    if 5 <= len(approx) <= 7:
                        has_hexagon = True
                        cv2.drawContours(display, [approx], -1, (255, 0, 0), 3)

            step_passed = has_hexagon
            status_text = f"Hexagon: {has_hexagon}"

        # ----------------------------------------------------
        # STEP 3 ~ STEP 4 (必要に応じて追加)
        # ----------------------------------------------------
        else:
            status_text = f"Step {current_step} in progress..."

        # ----------------------------------------------------
        # カウンタの更新とステップ進行
        # ----------------------------------------------------
        if step_passed:
            true_count += 1
        else:
            true_count = max(0, true_count - 1)  # 一瞬のブレで即0リセットしないための処理

        if true_count >= REQUIRED_TRUE_FRAMES:
            current_step += 1
            true_count = 0
            print(f"STEP CLEAR! Advanced to Step {current_step}")

        # ----------------------------------------------------
        # UI描画 (画面上のテキストオーバーレイ)
        # ----------------------------------------------------
        # 上部ステータスバー背景
        cv2.rectangle(display, (0, 0), (640, 80), (30, 30, 30), -1)
        
        # ステータス文字描画
        cv2.putText(display, f"STEP: {current_step}", (20, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        
        cv2.putText(display, status_text, (20, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # 進行度プログレスバー
        progress_width = int((true_count / REQUIRED_TRUE_FRAMES) * 200)
        cv2.rectangle(display, (400, 20), (600, 40), (100, 100, 100), 2)
        if progress_width > 0:
            cv2.rectangle(display, (400, 20), (400 + progress_width, 40), (0, 255, 0), -1)

        # ----------------------------------------------------
        # 画面表示 & キー入力処理（最重要）
        # ----------------------------------------------------
        cv2.imshow("Origami Step Assister", display)

        # キーの受付（1ms待機）
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('n'):  # デバッグ用：'n'キーで強制次ステップへ
            current_step += 1
            true_count = 0
            print(f"Forced skip to Step {current_step}")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
