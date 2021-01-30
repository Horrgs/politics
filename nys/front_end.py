from tkinter import *
from tkinter import ttk
from nys import scrape
from nys.scrape import GovtLevel


class Central:

    root = None
    frame = None
    advanced = False

    def __init__(self):
        root = Tk()
        root.title("Testing")
        root.geometry("1000x700")
        root.columnconfigure(0, weight=1)

        frame = ttk.Frame(root)
        context = Label(frame, text="Search State or County records.")

        def get_county():
            frame.destroy()
            return CountySearch(root)

        def get_state():
            frame.destroy()
            return None

        state = Button(frame, text='State', command=get_state)
        county = Button(frame, text='County', command=get_county)

        frame.grid(column=0, row=0)
        context.grid(column=0, row=0, columnspan=2)
        state.grid(column=0, row=1)
        county.grid(column=1, row=1)
        self.frame = frame
        self.root = root

    def is_advanced(self):
        return self.advanced

    def set_advanced_state(self, advanced):
        self.advanced = advanced
        
    def get_frame(self):
        return self.frame

    def get_root(self):
        return self.root


class CountySearch(Central):
    municipality = None

    def __init__(self, root):
        frame = ttk.Frame(root)
        counties = scrape.get_counties()
        counties = list(counties.keys())
        county_label = Label(frame, text='Select County: ')

        county = StringVar(frame)
        county.set("ALL")  # default value
        counties.insert(0, "ALL")

        util = Utils()
        w = OptionMenu(frame, county, *counties, command=lambda _: self.show_municipalities(county.get()))

        submit = Button(frame, text="Submit", command=lambda: ok(frame, county))
        frame.grid(column=0, row=0)
        county_label.grid(column=0, row=0)
        w.grid(column=1, row=0)
        submit.grid(column=0, row=1, columnspan=2)
        advanced = Button(frame,
                          text="Advanced Settings",
                          command=lambda: util.toggle_advanced_settings(self, GovtLevel.COUNTY))
        advanced.grid(column=0, row=2, columnspan=2)
        print(county.get())
        self.frame = frame
        self.root = root

    def show_municipalities(self, selection):
        if self.is_advanced():
            county = scrape.get_counties()
            municipalities = scrape.get_municipality(county[selection])
            municipalities = list(municipalities.keys())

            if self.municipality is not None:
                self.municipality.grid_forget()
            else:
                for widget in self.get_frame().winfo_children():
                    if 'row' in widget.grid_info() and widget.grid_info()['row'] > 0:
                        widget.grid(row=widget.grid_info()['row'] + 1, column=widget.grid_info()['column'])

                lbl_municipalities = Label(self.get_frame(), text="Municipalities: ")
                lbl_municipalities.grid(column=0, row=1)

            muni = StringVar(self.get_frame())
            muni.set("ALL")  # default value
            municipalities.insert(0, "ALL")
            self.municipality = OptionMenu(self.get_frame(), muni, *municipalities, command=get_selection)

            self.municipality.grid(column=1, row=1)



class Utils:

    def toggle_advanced_settings(self, program, govt_level):
        text = ""
        county = None
        program.set_advanced_state(not program.is_advanced())
        for widget in program.get_frame().winfo_children():
            if type(widget) is Button:
                if "Advanced Settings" in widget['text']:
                    if program.is_advanced():
                        text = "Hide Advanced Settings"
                    else:
                        text = "Advanced Settings"
                widget.grid_forget()

        if program.is_advanced():
            status_label = Label(program.get_frame(), text="Status: ")
            filer_label = Label(program.get_frame(), text="Filer: ")
            registered_label = Label(program.get_frame(), text="Registered Within: ")
            status_opt = ["ALL", "ACTIVE", "TERMINATED"]
            status_def = StringVar(program.get_frame())
            status_def.set(status_opt[1])
            status = OptionMenu(program.get_frame(), status_def, *status_opt)
            row = 1

            registered_opt = ["ALL", "Today", "Last 7 days", "Last 30 days", "Last Year", "Date Range"]
            registered_def = StringVar(program.get_frame())
            registered_def.set(registered_opt[0])
            registered = OptionMenu(program.get_frame(), registered_def, *registered_opt)

            filer_opt = ["ALL", "Candidate", "Committee"]
            filer_def = StringVar(program.get_frame())
            filer_def.set(filer_opt[0])
            filer = OptionMenu(program.get_frame(), filer_def, *filer_opt)

            status_label.grid(column=0, row=row)
            status.grid(column=1, row=row)
            row += 1

            if govt_level == GovtLevel.COUNTY:
                pass

            filer_label.grid(column=0, row=row)
            filer.grid(column=1, row=row)
            row += 1

            registered_label.grid(column=0, row=row)
            registered.grid(column=1, row=row)
            row += 1

            submit = Button(program.get_frame(), text="Submit", command=lambda: ok(program.get_frame(), {}))
            submit.grid(column=0, row=row, columnspan=2)
            row += 1
            advanced = Button(program.get_frame(), text=text,
                              command=lambda: self.toggle_advanced_settings(program, GovtLevel.COUNTY))
            advanced.grid(column=0, row=row, columnspan=2)
            print("The row of status label is {0}".format(status_label.grid_info()['row']))
        else:
            for item in program.root.winfo_children():
                item.grid_forget()
            return CountySearch(program.root)


def get_selection(item):
    print("Selected: {0}".format(item))


def ok(frame, variable):
    print("value is:" + variable.get())
    frame.destroy()




st = Central()
st.root.mainloop()
