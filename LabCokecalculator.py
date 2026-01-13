import tkinter as tk
import os
import sys
from tkinter import ttk, scrolledtext, messagebox, filedialog

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None


def calculate_cola():
    try:
        finished_volume = float(entry_volume.get() or 0)
        sevenx_ml = float(entry_sevenx.get() or 1000)
        waterbase_ml = float(entry_waterbase.get() or 1000)

        phosphoric_pct = float(entry_phos.get() or 85)
        acetic_pct = float(entry_acetic.get() or 5)

        no_caffeine = var_caffeine.get()
        vitamin_c = var_vitamin.get()
        reduce_sugar = var_sugar.get()

        scale_7x = sevenx_ml / 1000.0
        scale_water = waterbase_ml / 1000.0

        phos_ml_base = 45 * (85 / phosphoric_pct) if not vitamin_c else 0
        acetic_ml_base = 10 * (5 / acetic_pct)

        # === 精密天平需求判断（新逻辑）===
        need_precision = False
        precision_reason = []

        # 所有可能微量的固体成分（阈值统一5g：小于5g时普通厨房秤误差太大，需要0.01g或更高精度）
        micro_solids = []

        # 三氯蔗糖（仅最终组装）
        if reduce_sugar and finished_volume > 0:
            sucralose_g = round(52 / 600 * finished_volume, 4)
            if sucralose_g > 0:
                micro_solids.append((f"三氯蔗糖 {sucralose_g}g", sucralose_g))

        # 咖啡因
        caffeine_g = 0 if no_caffeine else 9.65 * scale_water
        if caffeine_g > 0:
            micro_solids.append((f"咖啡因 {caffeine_g:.3f}g", caffeine_g))

        # 葡萄酒单宁
        tannin_g = 8 * scale_water
        if tannin_g > 0:
            micro_solids.append((f"葡萄酒单宁 {tannin_g:.3f}g", tannin_g))

        # 维生素C（如果使用）
        vitamin_g = 300 * scale_water if vitamin_c else 0
        if vitamin_g > 0:
            micro_solids.append((f"抗坏血酸粉（维生素C） {vitamin_g:.3f}g", vitamin_g))

        # 柠檬酸（复合酸剂时）
        citric_g = 200 * scale_water if vitamin_c else 0
        if citric_g > 0 and citric_g < 5:  # 小批量时提醒
            micro_solids.append((f"柠檬酸 {citric_g:.3f}g", citric_g))



        # 判断：只要有任何固体 <5g，就需要精密天平
        for name, mass in micro_solids:
            if mass < 5:
                need_precision = True
                precision_reason.append(name)

        if need_precision:
            precision_label.config(text="⚠️ 精密天平需求 (0.01g或更高精度)\n原因: " + "; ".join(precision_reason),
                                   foreground="red", font=("Helvetica", 10, "bold"))
        else:
            precision_label.config(text="✓ 无需精密天平", foreground="green")

        # === 输出文本（保持不变）===
        result_text.delete(1.0, tk.END)

        version_str = ""
        if vitamin_c:
            version_str += "维生素C+柠檬酸复合版"
        else:
            version_str += "磷酸版"
        if no_caffeine:
            version_str += " 无咖啡因"
        else:
            version_str += " 含咖啡因"

        result_text.insert(tk.END, "=== LabCoke计算器 Ver0.0.1 ===\n")
        result_text.insert(tk.END, f"风味剂版本: {version_str}\n\n")

        # 1. 7X
        result_text.insert(tk.END, f"=== 1. 7X风味剂配制（{sevenx_ml:.1f} ml 浓缩） ===\n")
        result_text.insert(tk.END, f"柠檬精油: {45.8 * scale_7x:.3f} ml\n")
        result_text.insert(tk.END, f"青柠精油: {36.5 * scale_7x:.3f} ml\n")
        result_text.insert(tk.END, f"橙油: {1.2 * scale_7x:.3f} ml\n")
        result_text.insert(tk.END, f"茶树油: {8 * scale_7x:.3f} ml\n")
        result_text.insert(tk.END, f"肉豆蔻油: {2.7 * scale_7x:.3f} ml\n")
        result_text.insert(tk.END, f"香菜籽油: {0.7 * scale_7x:.3f} ml\n")
        result_text.insert(tk.END, f"葑醇: {0.6 * scale_7x:.3f} ml\n")
        result_text.insert(tk.END, f"食品级酒精: 补足至 {sevenx_ml:.1f} ml\n")
        result_text.insert(tk.END, "配制：混合所有成分，摇匀密封冷藏。\n\n")

        # 2. 水基
        # 2. 水基
        result_text.insert(tk.END, f"=== 2. 水基风味剂配制（{waterbase_ml:.1f} ml 浓缩） ===\n")
        result_text.insert(tk.END, f"醋精（{acetic_pct}%）: {acetic_ml_base * scale_water:.3f} ml\n")
        result_text.insert(tk.END, f"咖啡因: {'0 g' if no_caffeine else f'{9.65 * scale_water:.3f} g'}\n")
        result_text.insert(tk.END, f"甘油: {175 * scale_water:.3f} g\n")
        if vitamin_c:
            result_text.insert(tk.END, f"抗坏血酸粉（维生素C）: {100 * scale_water:.3f} g（成品约1g/L，每天饮用2升是安全的）\n")
            result_text.insert(tk.END, f"柠檬酸（食品级）： {200 * scale_water:.3f} g（补充尖锐酸感，复合酸剂）\n")
        else:
            result_text.insert(tk.END, f"磷酸（{phosphoric_pct}%）: {phos_ml_base * scale_water:.3f} ml\n")
        result_text.insert(tk.END, f"葡萄酒单宁: {8 * scale_water:.3f} g\n")
        result_text.insert(tk.END, f"焦糖色素: {320 * scale_water:.3f} ml\n")
        result_text.insert(tk.END, f"热水（初始）: 约 {200 * scale_water:.1f} ml\n")
        result_text.insert(tk.END, f"纯水: 补足至 {waterbase_ml:.1f} ml\n")
        result_text.insert(tk.END, "配制：热水溶解固体/液体 → 补水 → 密封冷藏。\n\n")
        # 3. 组装
        if finished_volume > 0:
            req_7x = finished_volume * 1
            req_water = finished_volume * 10
            sugar_g = 52 * finished_volume if reduce_sugar else 104 * finished_volume
            sucralose_g = round(52 / 600 * finished_volume, 4) if reduce_sugar else 0

            result_text.insert(tk.END, f"=== 3. 最终组装（{finished_volume} 升成品） ===\n")
            result_text.insert(tk.END,
                               f"所需7X: {req_7x:.2f} ml（配制了 {sevenx_ml:.1f} ml → {'够用' if sevenx_ml >= req_7x else '不足'}）\n")
            result_text.insert(tk.END,
                               f"所需水基: {req_water:.2f} ml（配制了 {waterbase_ml:.1f} ml → {'够用' if waterbase_ml >= req_water else '不足'}）\n")
            result_text.insert(tk.END, f"白砂糖: {sugar_g:.1f} g\n")
            if sucralose_g > 0:
                result_text.insert(tk.END, f"三氯蔗糖: {sucralose_g} g\n")
            result_text.insert(tk.END, f"溶糖热水参考: 约 {int(sugar_g * 2.5)} ml\n\n")

            result_text.insert(tk.END, "=== 组装流程 ===\n")
            if sucralose_g > 0:
                result_text.insert(tk.END, "1. 糖 + 三氯蔗糖 + 热水溶解\n")
            else:
                result_text.insert(tk.END, "1. 糖 + 热水溶解\n")
            result_text.insert(tk.END, f"2. 加所需7X {req_7x:.2f} ml + 水基 {req_water:.2f} ml\n")
            result_text.insert(tk.END, "3. 加盖加热至接近沸腾 \n")
            result_text.insert(tk.END, "4. 冷却 → 冷碳酸水稀释至目标体积\n")
            result_text.insert(tk.END, "5. 装瓶冷藏1~2d享用\n")

        result_text.insert(tk.END, "\n=== 注意事项 ===\n")
        result_text.insert(tk.END, "• 精油必须食品级\n")
        result_text.insert(tk.END, "• 小量固体需精密称量\n")
        result_text.insert(tk.END, "• 首次小批量测试口感\n")
        result_text.insert(tk.END, "• 本程序仅供娱乐,请勿将成品用于人体或动物,作者不对因此程序产生的任何后果负责\n")
        if  vitamin_c :
            result_text.insert(tk.END, "• 复合酸剂版：维生素C每天2升≤2g安全，柠檬酸无上限\n")

        if need_precision:
            result_text.insert(tk.END, "⚠️ 精密天平需求 (0.01g或更高精度)\n原因: " + "; ".join(precision_reason))



        # 为PDF准备
        global current_text, current_title
        title_parts = []
        if sevenx_ml > 0:
            title_parts.append(f"{sevenx_ml:.0f}ml 7X风味剂")
        if waterbase_ml > 0:
            title_parts.append(f"{waterbase_ml:.0f}ml 水基风味剂 ({version_str.strip()})")
        if finished_volume > 0:
            title_parts.append(f"{finished_volume}L 成品可乐")
        current_title = " / ".join(title_parts) + " 配制流程"
        current_text = result_text.get("1.0", tk.END)

    except ValueError:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "错误：请输入有效数字！")


def generate_pdf():
    try:
        from fpdf import FPDF
    except ImportError:
        messagebox.showerror("缺失依赖", "请先安装 fpdf2 库：\n\npip install fpdf2")
        return

    if not current_text.strip():
        messagebox.showwarning("无内容", "请先点击“计算全部配方”生成内容")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")],
        initialfile=current_title.replace("/", "_") + ".pdf"
    )
    if not file_path:
        return

    # 动态获取字体路径（支持打包后）
    def resource_path(relative_path):
        if hasattr(sys, '_MEIPASS'):  # PyInstaller打包后
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)  # 开发时

    font_path = resource_path("NotoSansSC-VariableFont_wght.ttf")

    if not os.path.exists(font_path):
        messagebox.showerror("字体缺失",
                             "字体文件 NotoSansSC-VariableFont_wght.ttf 未找到！\n请确保它在脚本同目录")
        return

    pdf = FPDF()
    pdf.add_page()

    # 添加字体
    pdf.add_font("NotoSansSC", "", font_path, uni=True)
    pdf.set_font("NotoSansSC", size=14)

    # 标题
    pdf.cell(0, 10, txt=current_title, ln=True, align="C")
    pdf.ln(10)

    # 正文
    pdf.set_font("NotoSansSC", size=10)
    for line in current_text.split("\n"):
        pdf.multi_cell(0, 6, txt=line)

    pdf.output(file_path)
    messagebox.showinfo("成功", f"PDF 已保存至：\n{file_path}")


# GUI（保持不变）
root = tk.Tk()
root.title("LabCoke计算器 Ver0.0.1 🍹")
root.geometry("960x1080")

frame_input = ttk.LabelFrame(root, text="参数 & 版本", padding=10)
frame_input.pack(fill="x", padx=10, pady=5)

ttk.Label(frame_input, text="7X风味剂配制体积 (ml):").grid(row=0, column=0, sticky="w")
entry_sevenx = ttk.Entry(frame_input, width=15)
entry_sevenx.grid(row=0, column=1);
entry_sevenx.insert(0, "1000")

ttk.Label(frame_input, text="水基风味剂配制体积 (ml):").grid(row=1, column=0, sticky="w")
entry_waterbase = ttk.Entry(frame_input, width=15)
entry_waterbase.grid(row=1, column=1);
entry_waterbase.insert(0, "1000")

ttk.Label(frame_input, text="成品体积（升，可留空）:").grid(row=2, column=0, sticky="w")
entry_volume = ttk.Entry(frame_input, width=15)
entry_volume.grid(row=2, column=1);
entry_volume.insert(0, "1")

ttk.Label(frame_input, text="原料磷酸浓度（%）:").grid(row=3, column=0, sticky="w")
entry_phos = ttk.Entry(frame_input, width=15)
entry_phos.grid(row=3, column=1);
entry_phos.insert(0, "85")

ttk.Label(frame_input, text="原料醋精浓度（%）:").grid(row=4, column=0, sticky="w")
entry_acetic = ttk.Entry(frame_input, width=15)
entry_acetic.grid(row=4, column=1);
entry_acetic.insert(0, "5")

var_sugar = tk.BooleanVar();
ttk.Checkbutton(frame_input, text="三氯蔗糖替代以减糖50%（仅组装）", variable=var_sugar).grid(row=5, columnspan=2, sticky="w")
var_caffeine = tk.BooleanVar();
ttk.Checkbutton(frame_input, text="去除咖啡因（水基）", variable=var_caffeine).grid(row=6, columnspan=2, sticky="w")
var_vitamin = tk.BooleanVar();
ttk.Checkbutton(frame_input, text="复合酸剂替换磷酸（水基）", variable=var_vitamin).grid(row=7, columnspan=2, sticky="w")

ttk.Button(frame_input, text="计算全部配方", command=calculate_cola).grid(row=8, column=0, columnspan=2, pady=10)

precision_label = ttk.Label(root, text="计算后显示...", foreground="gray")
precision_label.pack(pady=5)

ttk.Button(root, text="生成打印用 PDF 配方文档", command=generate_pdf).pack(pady=5)

result_text = scrolledtext.ScrolledText(root, width=110, height=52, font=("Courier", 10))
result_text.pack(padx=10, pady=10)

current_text = ""
current_title = "您的LabCoke配制流程"

calculate_cola()
root.mainloop()