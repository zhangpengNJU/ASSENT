import tkinter as tk
import tkinter.ttk as ttk
import Detailedgroundtruth
import TestGeneration
import AgreementIndicator
import groundtruth
class DemoApp:
    def  __init__(self, master):
        self.master = master
        self.nb = ttk.Notebook(self.master)
        self.page1 = groundtruth.Groundtruth(self.nb)
        #self.page2 = tk.Frame(self.nb)
        self.page2 = Detailedgroundtruth.Detailedgroundtruth(self.nb)
        self.page3 = TestGeneration.TestGeneration(self.nb)
        self.page4 = AgreementIndicator.Indicator(self.nb)
        self.nb.add(self.page1,text="Ground Truth")
        self.nb.add(self.page2,text="Detailed Ground Truth")
        self.nb.add(self.page3, text="Test Generation Approach")
        self.nb.add(self.page4, text="Agreement Indicator")
        self.create_widgets_page1()
        self.create_widgets_page2()
        self.create_widgets_page3()
        self.create_widgets_page4()
        self.nb.pack(expand=True,fill='both')

    def create_widgets_page1(self):
        self.lbl_page1 = tk.Label(self.page1, )
        self.lbl_page1.pack()

    def create_widgets_page2(self):
        self.lbl_page2 = tk.Label(self.page2,)
        self.lbl_page2.pack()

    def create_widgets_page3(self):
        self.lbl_page3 = tk.Label(self.page3,)
        self.lbl_page3.pack()

    def create_widgets_page4(self):
        self.lbl_page4 = tk.Label(self.page4,)
        self.lbl_page4.pack()

root = tk.Tk()
root.title("ASSENT: Design the experiment to find the most consistent MTE with Ground Truth")
app = DemoApp(root)
root.mainloop()