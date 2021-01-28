from tkinter import *
from tkinter import ttk
from nys import scrape
from nys.scrape import GovtLevel


def create_window():
    root = Tk()
    root.title("Testing")
    root.geometry("1000x700")
    root.columnconfigure(0, weight=1)
    return root


def create_home_screen(root):
    frame = ttk.Frame(root)
    context = Label(frame, text="Search State or County records.")

    def get_county():
        frame.destroy()
        return create_county_widget(root)

    def get_state():
        frame.destroy()
        return None

    state = Button(frame, text='State', command=get_state)
    county = Button(frame, text='County', command=get_county)

    frame.grid(column=0, row=0)
    context.grid(column=0, row=0, columnspan=2)
    state.grid(column=0, row=1)
    county.grid(column=1, row=1)
    return root


def create_county_widget(root):
    frame = ttk.Frame(root)
    counties = scrape.get_counties()
    counties = {str(name).split(".")[-1]: name.value for name in counties}
    county_label = Label(frame, text='Select County: ')

    county = StringVar(root)
    county.set("ALL")  # default value
    lst_counties = list(counties.keys())
    lst_counties.insert(0, "ALL")
    w = OptionMenu(frame, county, *lst_counties)
    submit = Button(frame, text="Submit", command=lambda: ok(frame, county))
    advanced = Button(frame, text="Advanced Settings", command=lambda: toggle_advanced_settings(root, frame, GovtLevel.COUNTY, True))
    frame.grid(column=0, row=0)
    county_label.grid(column=0, row=0)
    w.grid(column=1, row=0)
    submit.grid(column=0, row=1, columnspan=2)
    advanced.grid(column=0, row=2, columnspan=2)
    return root


def ok(frame, variable):
    print("value is:" + variable.get())
    frame.destroy()


def toggle_advanced_settings(root, frame, govt_level, to_show):
    submit = None
    advanced = None
    text = ""
    for widget in frame.winfo_children():

        if type(widget) is Button:
            if "Advanced Settings" in widget['text']:
                if to_show:
                    text = "Hide Advanced Settings"
                else:
                    text = "Show Advanced Settings"
            widget.grid_forget()
    if to_show:
        status_label = Label(frame, text="Status: ")
        filer_label = Label(frame, text="Filer: ")
        registered_label = Label(frame, text="Registered Within: ")
        status_opt = ["ALL", "ACTIVE", "TERMINATED"]
        status_def = StringVar(root)
        status_def.set(status_opt[0])
        status = OptionMenu(frame, status_def, *status_opt)
        row = 1

        registered_opt = ["ALL", "Today", "Last 7 days", "Last 30 days", "Last Year", "Date Range"]
        registered_def = StringVar(frame)
        status_def.set(registered_opt[0])
        registered = OptionMenu(frame, registered_def, *registered_opt)

        filer_opt = ["ALL", "Candidate", "Committee"]
        filer_def = StringVar(frame)
        filer_def.set(filer_opt[0])
        filer = OptionMenu(frame, filer_def, *filer_opt)

        status_label.grid(column=0, row=row)
        status.grid(column=1, row=row)
        row += 1

        if govt_level == GovtLevel.COUNTY:


        filer_label.grid(column=0, row=row)
        filer.grid(column=1, row=row)
        row += 1

        registered_label.grid(column=0, row=row)
        registered.grid(column=1, row=row)
        row += 1

        submit = Button(text="Submit", command=lambda: ok(frame, {}))
        submit.grid(column=0, row=row, columnspan=2)
        row += 1

        advanced = Button(text=text, command=lambda: toggle_advanced_settings(root, frame, not to_show))
        advanced.grid(column=0, row=row, columnspan=2)
        print("The row of status label is {0}".format(status_label.grid_info()['row']))
    else:
        for item in root.winfo_children():
            item.grid_forget()

        return create_county_widget(root)




main = create_window()
main = create_home_screen(main)
main.mainloop()
