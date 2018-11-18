import glob
import os
from typing import List, Tuple

from PIL import Image

# 基本となる縦横比(16:9)
DEFAULT_PIC_PER = 16.0 / 9.0

# 縦横比の判定用閾値
PIC_PER_THRESHOLD = 0.01


def get_crop_rect_for_default_pic_per(width: int, height: int) -> Tuple[int, int, int, int]:
    """基本となる縦横比(16:9)における、クロップする際のrectをピクセル単位で計算する

    :param width: 画像の横幅
    :param height: 画像の縦幅
    :return: rectを(X,Y,X+W,Y+H)形式のタプルで返す
    """

    # 定数定義
    RECT_X_PER = 20.0 / 1334.0
    RECT_Y_PER = 17.0 / 750.0
    RECT_W_PER = 942.0 / 1334.0
    RECT_H_PER = 715.0 / 750.0

    # ピクセルを計算するラムダ式
    func = lambda x, x_per: round(x * x_per)

    # 計算を行う
    X = func(width, RECT_X_PER)
    Y = func(height, RECT_Y_PER)
    W = func(width, RECT_W_PER)
    H = func(height, RECT_H_PER)

    return X, Y, X+W, Y+H


# ファイル一覧を読み込む
file_list: List[str] = glob.glob(os.path.join('input', '*.*'), recursive=True)

# 順番に処理する
for file_path in file_list:
    file_name, file_ext = os.path.splitext(os.path.basename(file_path))

    # 画像を読み込む
    image_data: Image = Image.open(file_path)

    # 縦横のピクセル値を取得する
    width, height = image_data.size

    """
    解析の考え方：
    複数のスクショを見る限りでは、次のようなレイアウトシステムだと推測される。
    ・ライブリザルトのRectについて、左上座標を(X, Y)・大きさをWxHとする
    ・ライブリザルトのRectの比率は、画像の縦横比が同じ場合は一定
    ・UIは16:9画面を基準に設計されており、
    　それより横長の場合はMVP表示・次へボタンを右にズラし、
    　それより縦長の場合は、ライブリザルトをセンタリング表示する
    ・ライブリザルト自体の縦横比は一定である
    このことから、解析の際は
    ・16:9画面については、割合によってクロップを行う
    ・それ以外の画面については、
    　横長の場合は右側の余った部分を切り落としたと仮定して上記操作、
    　縦長の場合はセンタリングで上下を切り落として上記操作
    　を行えばいい
    """

    # 画像の縦横比を判定する
    pic_type = 'default'
    pic_per = 1.0 * width / height
    if abs(DEFAULT_PIC_PER - pic_per) >= PIC_PER_THRESHOLD:
        if pic_per > DEFAULT_PIC_PER:
            pic_type = 'horizontally'
        else:
            pic_type = 'vertically'

    print(f'{file_path} : {width}x{height} {pic_type}')

    # 切り取るRectを算出する
    # (画像の縦横比によって挙動を分ける)
    rect = (0, 0, width, height)
    if pic_type == 'default':
        # 16:9の場合
        rect = get_crop_rect_for_default_pic_per(width, height)
    elif pic_type == 'horizontally':
        # 横長の場合
        width2 = height * DEFAULT_PIC_PER
        rect = get_crop_rect_for_default_pic_per(width2, height)
    else:
        # 縦長の場合
        height2 = width / DEFAULT_PIC_PER
        rect = get_crop_rect_for_default_pic_per(width, height2)
        height_offset = (height - height2) / 2
        rect = (rect[0], height_offset + rect[1], rect[2], height_offset + rect[3])
    print(rect)

    # 実際に切り取って保存する
    cropped_image_data: Image = image_data.crop(rect)
    cropped_image_data.save(os.path.join('output', file_name + '.png'))

print('処理終了')
