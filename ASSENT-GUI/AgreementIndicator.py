import tkinter as tk
import tkinter.ttk as ttk
import Detailedgroundtruth
import TestGeneration
class Indicator(tk.Frame):
    #options = ["Fault Detection", "Mutation Score", "Coverage Score", "Suite Size", ]
    options=[]
    indicator_vars = {}
    selected_options=[]
    sizegt=0
    buttonlist=[]

    def __init__(self,nb):
        super().__init__(nb)
        self.nb=nb






        self.button_init = tk.Button(self, text="Show available options", command=self.buttoninit)
        self.button_init.pack(pady=10)
        self.clear_button = tk.Button(self, text="Delete all options", command=self.clear_selection)
        self.clear_button.pack(pady=10)

        self.label_custom = tk.Label(self, text="Add your indicator")
        self.label_custom.pack()

        self.custom_text = tk.StringVar(self)
        self.entry_custom = tk.Entry(self, textvariable=self.custom_text)
        self.entry_custom.pack()
        self.button_add = tk.Button(self, text="Add indicator", command=self.add_custom_option)
        self.button_add.pack(pady=10)

        self.button = tk.Button(self, text="Generate complete experimental design", command=self.get_selection)
        self.button.pack(pady=10)
        self.label = tk.Label(self, text="Choose indicators：(If you have chosen multiple numerical ground truth, only OP can be used as the indicator.)")
        self.label.pack(pady=10)

        self.result = tk.Label(self, text="",fg="red")
        self.result.pack()


    def buttoninit(self):
        print(self.nb.nametowidget(self.nb.tabs()[1]).onlyOP)
        self.add_custom_option_txt("Kendall")
        self.add_custom_option_txt("Pearson")
        self.add_custom_option_txt("Spearman")
        self.add_custom_option_txt("R")
        self.add_custom_option_txt("Probabilistic Coupling")
        self.add_custom_option_txt("OP")

        if self.nb.nametowidget(self.nb.tabs()[1]).onlyOP == 1:

            for i in range(5):
                self.buttonlist[i].configure(state="disabled")

    def get_selection(self):
        #print(self.ground_truth_vars)
        #for option,var in self.ground_truth_vars.items():
        #    print(var.get())
        '''
        if self.indicator_vars["Suite Size"].get():
            self.sizegt=1
            self.nb.nametowidget(self.nb.tabs()[2]).sizegt=1
            self.nb.nametowidget(self.nb.tabs()[2]).check_button.configure(state="disabled")
            print("size!")
        else:
            self.sizegt = 0
            self.nb.nametowidget(self.nb.tabs()[2]).sizegt = 0
            self.nb.nametowidget(self.nb.tabs()[2]).check_button.configure(state="normal")
        '''
        try:
            s1=self.nb.nametowidget(self.nb.tabs()[1]).result_label.cget("text")
            s2 = self.nb.nametowidget(self.nb.tabs()[2]).result_label.cget("text")
            self.result.configure(text=s1+"\n"+s2[:-147]+"\nYour MTE is determined by yourself based on your research needs. Then using the selected indicators to find which MTE is the most consistent with the ground truth:")
        except:
            self.result.configure(text="Generation Failed. Please check the ground truth and test generation approach")
        '''
        selected_options = [option for option, var in self.indicator_vars.items() if var.get()]
        print("Selected options:", selected_options)
        self.selected_options=selected_options
        print(self.nb.tabs()[1])
        for s in selected_options:
            self.nb.nametowidget(self.nb.tabs()[1]).add_detail_option(s)
        #self.nb.tabs()[1].add_detail_option("fasfas")
        '''


    def add_custom_option_txt(self,txt):
        custom_option = txt
        self.options.append(custom_option)
        self.indicator_vars[custom_option] = tk.BooleanVar()
        check_button = tk.Checkbutton(self, text=custom_option, variable=self.indicator_vars[custom_option])
        check_button.pack(anchor="w")
        self.buttonlist.append(check_button)
        print("Added custom option:", custom_option)



    def add_custom_option(self):
        custom_option = self.custom_text.get()
        self.options.append(custom_option)
        if custom_option in self.indicator_vars:
            return 0
        self.indicator_vars[custom_option] = tk.BooleanVar()
        check_button = tk.Checkbutton(self, text=custom_option, variable=self.indicator_vars[custom_option])
        check_button.pack(anchor="w")
        print("Added custom option:", custom_option)





    def clear_selection(self):
        #selected_var.set(None)
        print("Selection cleared")
        for r in self.buttonlist:
            r.pack_forget()
        self.buttonlist=[]

