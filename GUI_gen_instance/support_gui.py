import customtkinter as ctk
import webbrowser

class OptionTopLevel(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x180")
        self.title("Options")
        self.attributes("-topmost", True)
        self.update()
        self.resizable(False, False)
        self.createWidgets()

    def saveOptions(self):
        logic_instance = self.master.winfo_toplevel().logic_instance
        logic_instance.path_to_dataset = self.newtorksDatasetVar.get()
        logic_instance.path_to_input_instances = self.benchmarkFolderVar.get()
        logic_instance.path_to_output_instances = self.outputFilePathVar.get()
        print("Options saved")
        self.destroy()

    def resetOptions(self):
        logic_instance = self.master.winfo_toplevel().logic_instance
        logic_instance.reset_options()
        self.newtorksDatasetVar.set(logic_instance.path_to_dataset)
        self.benchmarkFolderVar.set(logic_instance.path_to_input_instances)
        self.outputFilePathVar.set(logic_instance.path_to_output_instances)
        print("Options reset")

    def createWidgets(self):
        logic_instance = self.master.winfo_toplevel().logic_instance
        self.optionFrame = ctk.CTkFrame(self)
        self.optionFrame.columnconfigure(0, weight=1)
        self.optionFrame.columnconfigure(1, weight=4)
        self.optionFrame.pack(side="top", fill="both", expand=True)
        
        self.newtorksDatasetLabel = ctk.CTkLabel(self.optionFrame, text="Neural networks dataset")
        self.newtorksDatasetLabel.grid(row=0, column=0, padx=4, pady=5)
        self.newtorksDatasetVar = ctk.StringVar(value=logic_instance.path_to_dataset)
        self.newtorksEntry = ctk.CTkEntry(self.optionFrame, textvariable=self.newtorksDatasetVar)
        self.newtorksEntry.grid(row=0, column=1, padx=4, pady=5, sticky="ew")

        self.benchmarkFolderLabel = ctk.CTkLabel(self.optionFrame, text="Benchmarks folder")
        self.benchmarkFolderLabel.grid(row=1, column=0, padx=4, pady=5)
        self.benchmarkFolderVar = ctk.StringVar(value=logic_instance.path_to_input_instances)
        self.benchmarkFolderEntry = ctk.CTkEntry(self.optionFrame, textvariable=self.benchmarkFolderVar)
        self.benchmarkFolderEntry.grid(row=1, column=1, padx=4, pady=5, sticky="ew")

        self.outputFilePathLabel = ctk.CTkLabel(self.optionFrame, text="Output file path")
        self.outputFilePathLabel.grid(row=2, column=0, padx=4, pady=5)
        self.outputFilePathVar = ctk.StringVar(value=logic_instance.path_to_output_instances)
        self.outputFilePathEntry = ctk.CTkEntry(self.optionFrame, textvariable=self.outputFilePathVar)
        self.outputFilePathEntry.grid(row=2, column=1, padx=4, pady=5, sticky="ew")

        self.saveButton = ctk.CTkButton(self.optionFrame, text="Save", command=self.saveOptions)
        self.saveButton.grid(row=4, column=0, padx=4, pady=5)

        self.resetButton = ctk.CTkButton(self.optionFrame, text="Reset", command=self.resetOptions)
        self.resetButton.grid(row=4, column=1, padx=4, pady=5)

class SupportFrame(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        ctk.CTkFrame.__init__(self, master, *args, **kwargs, border_color="#000000", border_width=2)
        self.optionTopLevel = None
        self.createWidgets()

    def calculate(self):
        print("Calculate button clicked")
        self.winfo_toplevel().mainFrame.benchmarkScrollFrame.updateTabview()
        self.winfo_toplevel().logic_instance.prova()
    def show_options(self):
        if(self.optionTopLevel is None or not self.optionTopLevel.winfo_exists()):
            self.optionTopLevel = OptionTopLevel(master=self)
        
    def createWidgets(self):
        self.calculateButton = ctk.CTkButton(self, text="Calculate", command=self.calculate, width=0)
        self.calculateButton.grid(row=0, column=0, padx=4, pady=5)

        self.optionButton = ctk.CTkButton(self, text="Options", width=100, corner_radius=8, command=self.show_options)
        self.optionButton.grid(row=0, column=1, padx=4, pady=5)

        self.helpButton = ctk.CTkButton(self, text="Help", width=100, corner_radius=8, cursor="hand2")
        self.helpButton.grid(row=0, column=2, padx=4, pady=5)

        self.helpButton.bind("<Button-1>", lambda x: webbrowser.open_new(self.winfo_toplevel().logic_instance.help_url))