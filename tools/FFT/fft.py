import os
import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import librosa

from tkinter import Tk, filedialog


def a_weighting(f: np.ndarray) -> np.ndarray:
    """
    计算频率 f(Hz) 对应的 A 计权（单位：dB）
    IEC 61672 标准近似。
    增加对 0 Hz 的保护，避免除零。
    """
    f = np.array(f, dtype=float)

    # 避免 0 Hz 导致除零：将 0 替换为一个很小的正数
    f[f == 0] = 1e-6

    f_sq = f ** 2

    ra_num = (12200.0 ** 2) * (f_sq ** 2)
    ra_den = (
        (f_sq + 20.6 ** 2)
        * np.sqrt((f_sq + 107.7 ** 2) * (f_sq + 737.9 ** 2))
        * (f_sq + 12200.0 ** 2)
    )

    ra = ra_num / ra_den
    a = 20.0 * np.log10(ra) + 2.00
    return a


def process_audio_fft():
    """按照 fft.md 中的流程，对音频进行 FFT + A 计权，并导出图和 CSV/XLSX。"""
    # 关闭 Tk 主窗口，只使用文件/目录对话框
    root = Tk()
    root.withdraw()

    # 1. 弹出窗口, 询问声音文件的存储路径.
    audio_path = filedialog.askopenfilename(
        title="请选择声音文件",
        filetypes=[
            ("Audio files", "*.wav;*.mp3;*.flac;*.ogg;*.m4a"),
            ("All files", "*.*"),
        ],
    )
    if not audio_path:
        print("未选择声音文件，程序结束。")
        return

    # 2. 导入声音文件, 并进行快速傅里叶变换
    # 使用 librosa 统一读入为 float32, 单声道，保持原始采样率 sr=None
    data, fs = librosa.load(audio_path, sr=None, mono=True)
    data = data.astype(float)
    N = len(data)

    # 进行实数 FFT
    spectrum = np.fft.rfft(data)
    freqs = np.fft.rfftfreq(N, d=1.0 / fs)

    # 频谱幅度（线性）
    mag = np.abs(spectrum) + 1e-20  # 避免 log(0)

    # 将线性幅度转为 dB 标度（归一化到最大值）
    mag_db = 20.0 * np.log10(mag / np.max(mag))

    # A 计权处理
    a_db = a_weighting(freqs)
    mag_dba = mag_db + a_db

    # 只保留 0 ~ 20000 Hz
    f_max = 20000.0
    mask = (freqs >= 0.0) & (freqs <= f_max)
    freqs = freqs[mask]
    mag_db = mag_db[mask]
    mag_dba = mag_dba[mask]

    # 每 10 Hz 取 1 组数据（通过插值）
    f_step = 10.0
    f_plot = np.arange(0.0, f_max + f_step, f_step)
    dba_plot = np.interp(f_plot, freqs, mag_dba)
    db_plot = np.interp(f_plot, freqs, mag_db)

    # 3. 询问数据的保存路径
    save_dir = filedialog.askdirectory(title="请选择频谱数据的保存文件夹")
    if not save_dir:
        print("未选择保存目录，程序结束。")
        return

    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    today_str = datetime.datetime.now().strftime("%Y%m%d")
    out_name = f"{base_name}_{today_str}"

    csv_path = os.path.join(save_dir, out_name + ".csv")
    xlsx_path = os.path.join(save_dir, out_name + ".xlsx")

    # 4. 组织并保存数据
    # 左侧为原始 dB，右侧为 A 计权 dB(A)
    df = pd.DataFrame(
        {
            "Frequency_Hz": f_plot,
            "Level_dB": db_plot,
            "Level_dBA": dba_plot,
        }
    )

    # 保存为 CSV 和 XLSX
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    try:
        df.to_excel(xlsx_path, index=False)
    except Exception as e:
        print(f"保存 XLSX 失败：{e}")
    else:
        print(f"XLSX 已保存: {xlsx_path}")

    print(f"CSV 已保存: {csv_path}")

    # 5. 使用 matplotlib 导出频谱曲线
    plt.figure(figsize=(10, 5))

    # 光滑蓝色细实线
    plt.plot(f_plot, dba_plot, color="blue", linewidth=0.8, label="Spectrum dB(A)")

    # 纵坐标范围：最大值 + 5 dB(A)
    max_dba = float(np.max(dba_plot))
    min_dba = float(np.min(dba_plot))
    plt.ylim([min_dba - 5.0, max_dba + 5.0])

    # 横坐标 0 ~ 20000 Hz
    plt.xlim([0.0, f_max])

    plt.grid(True)
    plt.legend()

    # 坐标轴标题
    plt.xlabel("Frequency(Hz)")
    # 题中要求：纵坐标为声音的幅值 dB(A)，显示文字 mm/s
    plt.ylabel("Sound Level dB(A) (mm/s)")

    # 找峰值并标注：显示频率和噪音值
    peak_idx = int(np.argmax(dba_plot))
    peak_f = float(f_plot[peak_idx])
    peak_val = float(dba_plot[peak_idx])

    text = f"Peak: {peak_f:.1f} Hz, {peak_val:.1f} dB(A)"
    plt.annotate(
        text,
        xy=(peak_f, peak_val),
        xytext=(peak_f + 500.0, peak_val),
        arrowprops=dict(arrowstyle="->", color="red"),
        fontsize=9,
        color="red",
    )

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    process_audio_fft()

