import tkinter as tk
import tkinter.ttk as ttk
#import groundtruth
class Detailedgroundtruth(tk.Frame):
    onlyOP=0
    def __init__(self,nb,selected_options=[]):
        super().__init__(nb)
        self.selected_options=selected_options
        self.radio_button={}
        for option in self.selected_options:
            self.add_detail_option(option)
        self.clear_button = tk.Button(self, text="Delete all the Detailed Ground Truth options", command=self.clear_selection)
        self.clear_button.pack(pady=10)
        self.generate_detailedgt = tk.Button(self, text="Generate Detailed Ground Truth", command=self.generate_sentence)
        self.generate_detailedgt.pack(pady=10)

        self.label = tk.Label(self, text="Refine your Ground Truth:\n Do you think it is the numerical size (e.g., A kills more mutants than B) that determines the strength \nor the need for subsuming relationships(e.g., B only kills a subset of A's killed mutant set)?")
        self.label.pack(pady=10)
        self.result_label = tk.Label(self, text="")
        self.result_label.pack()



    def add_detail_option(self,option):
        selected_var1 = tk.StringVar(self)
        selected_var1.set("none_selected")
        radio_button1 = tk.Radiobutton(self, text=option+": The numerical values determine the strength relationship", variable=selected_var1, value=1)
        radio_button1.pack(anchor="w")

        radio_button2 = tk.Radiobutton(self, text=option+": The subsuming relationship determines the strength relationship", variable=selected_var1, value=2)
        radio_button2.pack(anchor="w")
        self.radio_button[radio_button1]=selected_var1
        self.radio_button[radio_button2]=selected_var1

    def clear_selection(self):
        #selected_var.set(None)
        print("Selection cleared")
        for r in self.radio_button:
            r.pack_forget()
        self.radio_button={}



    def generate_sentence(self):
        try:
            # print(self.radio_button)
            # selected_options = [option for option,var in self.radio_button.items() if var.get()]
            # print(selected_options)
            sentence = "Your ground truth is: A is more effective than B if and only if "
            i = 0
            for option, var in self.radio_button.items():
                # print(var.get())
                # print("i"+str(i))
                if i % 2 == 1:
                    i = i + 1
                    continue
                if int(var.get()) == 1:
                    s = option.cget("text")
                    op = s.split(":")[0]
                    sentence += "A's " + op + " is bigger than B's, and "
                if int(var.get()) == 2:
                    s = option.cget("text")
                    op = s.split(":")[0]
                    sentence += "A's " + op + " subsumes B's, and "
                i = i + 1
            sentence = sentence[:-6] + "."
            self.result_label.configure(text=sentence)
            if sentence.count("bigger than ") > 1:
                self.onlyOP = 1
            else:
                self.onlyOP = 0
            return sentence
        except:
            self.result_label.configure(text="Please select a detail for each ground truth.")
        '''
        if selected_options==[]:
            self.result_label.configure(text="")
            return ""
        sentence = "Your ground truth is: A is more effective than B if and only if "
        for s in selected_options:
            print(s.cget("text"))
            s=s.cget("text")
            op=s.split(":")[0]
            print(op)
            if "numerical" in s:
                sentence+="A's "+op+" is bigger than B's, "
            else:
                sentence += "A's " + op + " subsumes B's, "
        self.result_label.configure(text=sentence)
        return sentence
'''


    def add_custom_option(self):
        custom_option = self.custom_text.get()
        self.options.append(custom_option)
        if custom_option in self.ground_truth_vars:
            return 0
        self.ground_truth_vars[custom_option] = tk.BooleanVar()
        check_button = tk.Checkbutton(self, text=custom_option, variable=self.ground_truth_vars[custom_option])
        check_button.pack(anchor="w")
        print("Added custom option:", custom_option)
