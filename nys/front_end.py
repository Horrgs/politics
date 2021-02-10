from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry
from nys import scrape
from nys.scrape import *


class Central:
    root, frame = None, None
    advanced = False

    def __init__(self):
        root = Tk()
        root.title("Testing")
        root.geometry("1000x700")
        root.columnconfigure(0, weight=1)

        frame = ttk.Frame(root)
        context = Label(frame, text="Search State or County records.")

        def update_search(govt_level):
            search = Search(govt_level)
            frame.destroy()
            if govt_level == GovtLevel.COUNTY:
                CountySearch(search, self).county_search()

        state = Button(frame, text='State', command=lambda: update_search(GovtLevel.STATE))
        county = Button(frame, text='County', command=lambda: update_search(GovtLevel.COUNTY))

        frame.grid(column=0, row=0)
        context.grid(column=0, row=0, columnspan=2)
        state.grid(column=0, row=1)
        county.grid(column=1, row=1)
        self.frame = frame
        self.root = root


class CountySearch:
    municipality = None
    central = None
    search = None

    def __init__(self, search: Search, central: Central):
        self.search = search
        self.central = central

    def county_search(self):
        self.central.frame.destroy()

        frame = ttk.Frame(self.central.root)
        counties = scrape.get_counties()
        county_label = Label(frame, text='Select County: ')

        county = StringVar(frame)
        county.set(self.search.county)

        util = Utils()

        def post_county():
            if county.get() != "ALL":
                return {
                    "name": county.get(),
                    "id": counties[county.get()]
                }
            else:
                return {
                    "name": county.get()
                }

        counties_lst = list(counties.keys())
        counties_lst.insert(0, "ALL")

        county_selection = OptionMenu(frame, county, *counties_lst, command=lambda _:
                                      util.show_municipalities(self.central, self.search, post_county()))

        submit_btn = Button(frame, text="Submit", command=lambda: submit(self.search))
        advanced = Button(frame, text="Advanced Settings", command=lambda:
                          util.toggle_advanced_settings(self.central, self.search))

        frame.grid(column=0, row=0)
        county_label.grid(column=0, row=0)
        county_selection.grid(column=1, row=0)
        submit_btn.grid(column=0, row=1, columnspan=2)
        advanced.grid(column=0, row=2, columnspan=2)
        self.central.frame = frame
        return self.central.frame


class Utils:
    lbl_municipalities = None
    municipality = None

    date_from_cal, date_to_cal = None, None
    date_from_lbl, date_to_lbl = None, None

    def show_municipalities(self, central, search, county_data):
        search.update('county', county_data['name'])
        if 'id' in county_data:
            search.update('county_id', county_data['id'])
        else:
            search.update('county_id', None)
        if central.advanced:
            if county_data['name'].lower() == "ALL".lower():
                self.municipality.grid_forget()
                self.lbl_municipalities.grid_forget()
            else:
                municipalities = scrape.get_municipality(scrape.get_counties()[county_data['name']])



                if self.municipality is not None:
                    self.municipality.grid_forget()
                    self.lbl_municipalities.grid_forget()
                else:
                    for widget in central.frame.winfo_children():
                        if 'row' in widget.grid_info() and widget.grid_info()['row'] > 0:
                            widget.grid(row=widget.grid_info()['row'] + 1, column=widget.grid_info()['column'])

                self.lbl_municipalities = Label(central.frame, text="Municipalities: ")
                self.lbl_municipalities.grid(column=0, row=1)

                municipality = StringVar(central.frame)
                municipality.set("ALL")  # default value

                def post_municipalities():
                    search.update('municipality', municipality.get())
                    if municipality.get() != "ALL":
                        search.update('municipality_id', municipalities[municipality.get()])
                    else:
                        search.update('municipality_id', None)
                    print(municipality.get())

                municipalities_lst = list(municipalities.keys())
                municipalities_lst.insert(0, "ALL")
                self.municipality = OptionMenu(central.frame, municipality, *municipalities_lst,
                                               command=lambda _: post_municipalities())
                self.municipality.grid(column=1, row=1)



    def toggle_advanced_settings(self, central, search):
        advanced_btn, submit_btn = None, None
        central.advanced = (not central.advanced)

        for widget in central.frame.winfo_children():
            if type(widget) is Button:
                if "submit" in widget['text'].lower():
                    submit_btn = widget
                elif "advanced settings" in widget['text'].lower():
                    advanced_btn = widget
                widget.grid_forget()

        if central.advanced:
            status_label = Label(central.frame, text="Status: ")
            filer_label = Label(central.frame, text="Filer: ")
            registered_label = Label(central.frame, text="Registered Within: ")

            status_opt = [e.name.title() for e in Status]
            status_def = StringVar(central.frame)
            status_def.set(search.status)
            status = OptionMenu(central.frame, status_def, *status_opt,
                                command=lambda _: search.update('status', status_def.get()))
            row = 1

            registered_opt = [e.name.replace("_", " ").title() for e in Registered]
            registered_def = StringVar(central.frame)
            registered_def.set(search.registered)
            registered = OptionMenu(central.frame, registered_def, *registered_opt,
                                    command=lambda _: self.date_range(search, central, registered_def.get()))

            filer_opt = [e.name.title() for e in Filer]
            filer_def = StringVar(central.frame)
            filer_def.set(search.filer)
            filer = OptionMenu(central.frame, filer_def, *filer_opt,
                               command=lambda _: search.update('filer', filer_def.get()))

            status_label.grid(column=0, row=row)
            status.grid(column=1, row=row)
            row += 1

            filer_label.grid(column=0, row=row)
            filer.grid(column=1, row=row)
            row += 1

            registered_label.grid(column=0, row=row)
            registered.grid(column=1, row=row)
            row += 1

            submit_btn.grid(column=0, row=row, columnspan=2)
            row += 1
            advanced_btn.config(text="Hide Advanced Settings")
            advanced_btn.grid(column=0, row=row, columnspan=2)
            print("The row of status label is {0}".format(status_label.grid_info()['row']))

            if search.county != "ALL":
                self.show_municipalities(central, search, search.county)

        else:
            for item in central.root.winfo_children():
                item.grid_forget()
            return CountySearch(search, central).county_search()



    def date_range(self, search, central, selection):
        search.update('registered', selection)
        last_row = 0

        if selection == "Date Range":
            for widget in central.frame.winfo_children():
                if 'row' in widget.grid_info():
                    if type(widget) is not Button:
                        if last_row < widget.grid_info()['row']:
                            last_row = widget.grid_info()['row'] + 1
                    else:
                        widget.grid(row=(widget.grid_info()['row'] + 2))
            print("Last Row: {0}".format(last_row))

            self.date_from_lbl = Label(central.frame, text="Date From: ")
            self.date_to_lbl = Label(central.frame, text="Date To: ")

            self.date_from_cal = DateEntry(central.frame)
            self.date_from_cal.bind("<<DateEntrySelected>>", lambda _:
                                    search.update(Registered.DATE_RANGE, 'dateFrom', date=self.date_from_cal.get()))

            self.date_to_cal = DateEntry(central.frame)
            self.date_to_cal.bind("<<DateEntrySelected>>", lambda _:
                                  search.update(Registered.DATE_RANGE, 'dateTo', date=self.date_to_cal.get()))

            self.date_from_lbl.grid(column=0, row=last_row)
            self.date_from_cal.grid(column=1, row=last_row)
            last_row += 1

            self.date_to_lbl.grid(column=0, row=last_row)
            self.date_to_cal.grid(column=1, row=last_row)
        else:
            if self.date_from_cal is not None:
                self.date_from_cal.grid_forget()
                self.date_to_cal.grid_forget()
                self.date_to_lbl.grid_forget()
                self.date_from_lbl.grid_forget()


def submit(search):
    print(get_filers_v(search))


st = Central()
st.root.mainloop()
