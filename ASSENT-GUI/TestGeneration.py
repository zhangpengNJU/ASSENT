import tkinter as tk
import tkinter.ttk as ttk

class TestGeneration(tk.Frame):
    tg_vars={}
    radio_button = {}
    def __init__(self,nb,sizegt=0):
        super().__init__(nb)
        self.sizegt=sizegt
        self.add_sampling_option()
        #self.add_custom_option_txt("Randomly sampling")
        #self.add_custom_option_txt("Gredily samlping")
        self.add_custom_option_txt("Size Control",self.sizegt)
        self.generate_detailedgt = tk.Button(self, text="Generate Sampling Approach", command=self.generate_sentence)
        self.generate_detailedgt.pack(pady=10)
        self.result_label = tk.Label(self, text="")
        self.result_label.pack()





    def add_custom_option_txt(self,txt,bool1):
        custom_option = txt
        #self.options.append(custom_option)
        self.tg_vars[custom_option] = tk.BooleanVar()
        self.check_button = tk.Checkbutton(self, text=custom_option, variable=self.tg_vars[custom_option])
        if bool1:
            self.check_button.configure(state="disabled")  # 如果bool1为True，设置复选框不可选
        self.check_button.pack(anchor="w")
        print("Added custom option:", custom_option)


    def add_sampling_option(self):
        selected_var1 = tk.StringVar(self)
        selected_var1.set("none_selected")
        radio_button1 = tk.Radiobutton(self, text="Randomly sampling", variable=selected_var1, value=1)
        radio_button1.pack(anchor="w")

        radio_button2 = tk.Radiobutton(self, text="Greedily samlping", variable=selected_var1, value=2)
        radio_button2.pack(anchor="w")
        self.radio_button[radio_button1]=selected_var1
        self.radio_button[radio_button2]=selected_var1




    def generate_sentence(self):
        #print(self.radio_button)
        #selected_options = [option for option,var in self.radio_button.items() if var.get()]
        #print(selected_options)
        sentence = "Your sampling approach is: "
        i=0
        for option,var in self.radio_button.items():
            #print(var.get())
            #print("i"+str(i))
            if i%2==1:
                i = i + 1
                continue
            if int(var.get())==1:
                #s = option.cget("text")
                #op = s.split(":")[0]
                sentence += "Randomly sampling test suites among the test case pool "
            else:
                sentence += "Greedily samlping test suites among the test case pool "
            i = i + 1
        #print(self.tg_vars["Size Control"].get())
        if not self.tg_vars["Size Control"].get():
        #if self.sizegt==1:
            sentence+= "without size control.(If you have chosen size as ground truth, you can not sampling the test suites with the same size. You only compare the suite with different size.)"
        else:
            sentence += "with size control.(If you have chosen size as ground truth, you can not sampling the test suites with the same size. You only compare the suite with different size.)"
        self.result_label.configure(text=sentence)
        return sentence
