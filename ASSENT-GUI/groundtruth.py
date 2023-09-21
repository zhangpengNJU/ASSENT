import tkinter as tk
#import tkinter.ttk as ttk
#import Detailedgroundtruth
#import TestGeneration
#import AgreementIndicator
class Groundtruth(tk.Frame):
    #options = ["Fault Detection", "Mutation Score", "Coverage Score", "Suite Size", ]
    options=[]
    ground_truth_vars = {}
    selected_options=[]
    sizegt=0

    def __init__(self,nb):
        super().__init__(nb)
        self.nb=nb


        self.label_custom = tk.Label(self, text="Add your ground truth, e.g., 0.5*(Mutation Score)+0.5(Coverage Score)")
        self.label_custom.pack()

        self.custom_text = tk.StringVar(self)
        self.entry_custom = tk.Entry(self, textvariable=self.custom_text)
        self.entry_custom.pack()
        self.button_add = tk.Button(self, text="Add option", command=self.add_custom_option)
        self.button_add.pack(pady=10)

        self.button = tk.Button(self, text='Generate options in "Detailed Ground Truth"', command=self.get_selection)
        self.button.pack(pady=10)

        self.label = tk.Label(self, text="Choose your Ground Truth:\n (When comparing two test suites A and B, which combination of options can yield the most accurate conclusion?)")
        self.label.pack(pady=10)

        self.add_custom_option_txt("Fault Detection")
        self.add_custom_option_txt("Mutation Score")
        self.add_custom_option_txt("Coverage Score")
        self.add_custom_option_txt("Suite Size")


    def get_selection(self):
        #print(self.ground_truth_vars)
        #for option,var in self.ground_truth_vars.items():
        #    print(var.get())
        if self.ground_truth_vars["Suite Size"].get():
            self.sizegt=1
            self.nb.nametowidget(self.nb.tabs()[2]).sizegt=1
            self.nb.nametowidget(self.nb.tabs()[2]).check_button.configure(state="disabled")
            print("size!")
        else:
            self.sizegt = 0
            self.nb.nametowidget(self.nb.tabs()[2]).sizegt = 0
            self.nb.nametowidget(self.nb.tabs()[2]).check_button.configure(state="normal")

        selected_options = [option for option, var in self.ground_truth_vars.items() if var.get()]
        print("Selected options:", selected_options)
        self.selected_options=selected_options
        print(self.nb.tabs()[1])
        for s in selected_options:
            self.nb.nametowidget(self.nb.tabs()[1]).add_detail_option(s)
        #self.nb.tabs()[1].add_detail_option("fasfas")

    def add_custom_option_txt(self,txt):
        custom_option = txt
        self.options.append(custom_option)
        self.ground_truth_vars[custom_option] = tk.BooleanVar()
        check_button = tk.Checkbutton(self, text=custom_option, variable=self.ground_truth_vars[custom_option])
        check_button.pack(anchor="w")
        print("Added custom option:", custom_option)



    def add_custom_option(self):
        custom_option = self.custom_text.get()
        self.options.append(custom_option)
        if custom_option in self.ground_truth_vars:
            return 0
        self.ground_truth_vars[custom_option] = tk.BooleanVar()
        check_button = tk.Checkbutton(self, text=custom_option, variable=self.ground_truth_vars[custom_option])
        check_button.pack(anchor="w")
        print("Added custom option:", custom_option)




'''


class DemoApp:
    def  __init__(self, master):
        self.master = master
        self.nb = ttk.Notebook(self.master)
        self.page1 = Groundtruth(self.nb)
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
app = DemoApp(root)
root.mainloop()
'''