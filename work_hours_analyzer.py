import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
import os

# 设置matplotlib支持中文
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
matplotlib.rcParams['axes.unicode_minus'] = False

class WorkHoursAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏主窗口
        self.df = None
        self.filtered_df = None
        self.summary_df = None
        self.date_range = None
        
    def select_csv_file(self):
        """弹出窗口选择CSV文件"""
        messagebox.showinfo("提示", "请选择需要导入的CSV文件")
        file_path = filedialog.askopenfilename(
            title="选择CSV文件",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        return file_path
    
    def load_csv(self, file_path):
        """加载CSV文件并设置第一行为列名"""
        try:
            self.df = pd.read_csv(file_path, encoding='utf-8')
            # 如果第一行不是列名，可以尝试使用第一行作为列名
            # 这里假设CSV文件第一行就是列名
            return True
        except UnicodeDecodeError:
            try:
                self.df = pd.read_csv(file_path, encoding='gbk')
                return True
            except Exception as e:
                messagebox.showerror("错误", f"读取文件失败: {str(e)}")
                return False
        except Exception as e:
            messagebox.showerror("错误", f"读取文件失败: {str(e)}")
            return False
    
    def convert_date_column(self):
        """将'记录日期'列转换为日期格式"""
        if '记录日期' not in self.df.columns:
            messagebox.showerror("错误", "数据表中未找到'记录日期'列")
            return False
        
        try:
            # 尝试多种日期格式
            self.df['记录日期'] = pd.to_datetime(self.df['记录日期'], errors='coerce')
            # 检查是否有无法转换的日期
            if self.df['记录日期'].isna().any():
                messagebox.showwarning("警告", "部分日期数据无法转换，已标记为NaN")
            return True
        except Exception as e:
            messagebox.showerror("错误", f"日期转换失败: {str(e)}")
            return False
    
    def get_date_range(self):
        """弹出窗口要求录入日期范围"""
        messagebox.showinfo(
            "日期格式提示",
            "请输入日期范围，格式为：YYYY-MM-DD\n例如：2024-01-01"
        )
        
        start_date_str = simpledialog.askstring(
            "输入日期范围",
            "请输入开始日期 (格式: YYYY-MM-DD):"
        )
        
        if start_date_str is None:
            return None, None
        
        end_date_str = simpledialog.askstring(
            "输入日期范围",
            "请输入结束日期 (格式: YYYY-MM-DD):"
        )
        
        if end_date_str is None:
            return None, None
        
        try:
            start_date = pd.to_datetime(start_date_str)
            end_date = pd.to_datetime(end_date_str)
            self.date_range = (start_date_str, end_date_str)
            return start_date, end_date
        except Exception as e:
            messagebox.showerror("错误", f"日期格式错误: {str(e)}\n请使用格式: YYYY-MM-DD")
            return None, None
    
    def filter_by_date_range(self, start_date, end_date):
        """根据日期范围筛选数据"""
        try:
            mask = (self.df['记录日期'] >= start_date) & (self.df['记录日期'] <= end_date)
            self.filtered_df = self.df[mask].copy()
            return True
        except Exception as e:
            messagebox.showerror("错误", f"数据筛选失败: {str(e)}")
            return False
    
    def aggregate_data(self):
        """按照'记录人员'和'项目名称'分组，对'工时数'求和"""
        required_columns = ['记录人员', '项目名称', '工时数']
        missing_columns = [col for col in required_columns if col not in self.filtered_df.columns]
        
        if missing_columns:
            messagebox.showerror("错误", f"数据表中缺少以下列: {', '.join(missing_columns)}")
            return False
        
        try:
            # 确保工时数列是数值类型
            self.filtered_df['工时数'] = pd.to_numeric(self.filtered_df['工时数'], errors='coerce')
            
            # 分组聚合
            self.summary_df = self.filtered_df.groupby(['记录人员', '项目名称'])['工时数'].sum().reset_index()
            self.summary_df.columns = ['记录人员', '项目名称', '工时数求和']
            return True
        except Exception as e:
            messagebox.showerror("错误", f"数据聚合失败: {str(e)}")
            return False
    
    def save_file(self):
        """弹出窗口询问保存路径和名称"""
        if self.summary_df is None:
            messagebox.showerror("错误", "没有可保存的数据")
            return None
        
        # 生成默认文件名
        if self.date_range:
            date_part = f"{self.date_range[0]}_to_{self.date_range[1]}"
        else:
            date_part = "unknown_date"
        
        current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        default_filename = f"工时统计_{date_part}_{current_time}.xlsx"
        
        file_path = filedialog.asksaveasfilename(
            title="保存文件",
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")],
            initialfile=default_filename
        )
        
        if file_path:
            try:
                self.summary_df.to_excel(file_path, index=False, engine='openpyxl')
                return file_path
            except Exception as e:
                messagebox.showerror("错误", f"保存文件失败: {str(e)}")
                return None
        return None
    
    def generate_chart(self, file_path):
        """生成统计图表"""
        if self.summary_df is None:
            messagebox.showerror("错误", "没有可用的数据")
            return
        
        try:
            # 创建图表
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # 准备数据：透视表格式
            pivot_data = self.summary_df.pivot_table(
                index='记录人员',
                columns='项目名称',
                values='工时数求和',
                fill_value=0
            )
            
            # 绘制分组柱状图
            pivot_data.plot(kind='bar', ax=ax, width=0.8)
            
            ax.set_xlabel('记录人员', fontsize=12)
            ax.set_ylabel('工时数求和', fontsize=12)
            ax.set_title('每个人员在每个项目上的工时统计', fontsize=14, fontweight='bold')
            ax.legend(title='项目名称', bbox_to_anchor=(1.05, 1), loc='upper left')
            ax.grid(axis='y', alpha=0.3)
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # 保存图表
            chart_path = file_path.replace('.xlsx', '_图表.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.show()
            
            messagebox.showinfo("成功", f"图表已保存至: {chart_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"生成图表失败: {str(e)}")
    
    def run(self):
        """运行主程序"""
        try:
            # 步骤1: 选择CSV文件
            csv_path = self.select_csv_file()
            if not csv_path:
                messagebox.showinfo("提示", "未选择文件，程序退出")
                return
            
            # 步骤2: 加载CSV文件
            if not self.load_csv(csv_path):
                return
            
            # 步骤3: 转换日期格式
            if not self.convert_date_column():
                return
            
            # 步骤4: 获取日期范围
            start_date, end_date = self.get_date_range()
            if start_date is None or end_date is None:
                messagebox.showinfo("提示", "未输入日期范围，程序退出")
                return
            
            # 步骤5: 筛选数据
            if not self.filter_by_date_range(start_date, end_date):
                return
            
            messagebox.showinfo("提示", f"筛选后数据共 {len(self.filtered_df)} 条记录")
            
            # 步骤6: 数据聚合
            if not self.aggregate_data():
                return
            
            # 步骤7: 保存文件
            saved_path = self.save_file()
            if not saved_path:
                messagebox.showinfo("提示", "未保存文件，程序退出")
                return
            
            messagebox.showinfo("成功", f"数据已保存至: {saved_path}")
            
            # 步骤8: 生成图表
            self.generate_chart(saved_path)
            
        except Exception as e:
            messagebox.showerror("错误", f"程序运行出错: {str(e)}")
        finally:
            self.root.destroy()

if __name__ == "__main__":
    app = WorkHoursAnalyzer()
    app.run()


