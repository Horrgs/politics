from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry
from nys import scrape
from nys.medium import Entity
from nys.scrape import *


class Central:
    root, frame = None, None
    advanced = False

    def __init__(self):

        # initialize the program and layout
        root = Tk()
        root.title("Testing")
        root.geometry("1000x700")
        root.columnconfigure(0, weight=1)

        frame = ttk.Frame(root)
        context = Label(frame, text="Search State or County records.")

        """ update_search takes a GovtLevel (County or State) and populates the frame to do a search for the 
        corresponding GovtLevel. """

        def update_search(govt_level):
            search = Search(govt_level)
            frame.destroy()
            if govt_level == GovtLevel.COUNTY:
                CountySearch(search, self).county_search()

        # populates frame with the corresponding GovtLevel using update search.
        state = Button(frame, text='State', command=lambda: update_search(GovtLevel.STATE))
        county = Button(frame, text='County', command=lambda: update_search(GovtLevel.COUNTY))

        # frame layout
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
        # destroy current frame to repopulate with new frame
        self.central.frame.destroy()

        frame = ttk.Frame(self.central.root, name="county")

        # populate frame with county widgets
        counties = scrape.get_counties()
        if counties is None:
            return self.county_search()
        else:
            counties_lst = list(counties.keys())
        county_label = Label(frame, text='Select County: ')

        util = Utils()

        counties_lst.insert(0, "All")

        county_selection = ttk.Combobox(frame, values=counties_lst)
        county_selection.set(counties_lst[0])

        # update current county selection, if county is specific (i.e. not all), set the county_id, else null it.
        def post_county(search):

            search.update('county', county_selection.get())
            if county_selection.get() != "ALL":
                search.update('county_id', counties[county_selection.get()])
            else:
                search.update('county_id', None)

            if self.central.advanced:
                util.show_municipalities(self.central, self.search)

        county_selection.bind('<<ComboboxSelected>>', lambda _: post_county(self.search))

        submit_btn = Button(frame, text="Submit", command=lambda: display_filers(self.search, self.central))
        advanced = Button(frame, text="Advanced Settings", command=lambda:
        util.toggle_advanced_settings(self.central, self.search))


        # layout frame
        frame.grid(column=0, row=0)
        county_label.grid(column=0, row=0, sticky='w')
        county_selection.grid(column=1, row=0)
        submit_btn.grid(column=0, row=1, columnspan=2)
        advanced.grid(column=0, row=2, columnspan=2)
        self.central.frame = frame
        return self.central.frame


class Utils:

    date_from_cal, date_to_cal = None, None
    date_from_lbl, date_to_lbl = None, None

    # this is called when a county selection is made, but may not always show.
    def show_municipalities(self, central, search):
        # municipalities selection will only show if advanced settings has been selected.
        if central.advanced:

            """
            Check if county selection is all - if so, remove the widgets from frame.
            Check if municipality already exists - if so, remove it. 
            
            This is done because if county selection is all, you can't pick a municipality. If the municipality
            already exists, it gets removed because it may need to be populated with the results of a new county
             selection, if county selection isn't already all. """

            try:
                if search.county.lower() == "all" or central.root.nametowidget('county.municipality') is not None:
                    central.root.nametowidget('county.lbl_municipalities').grid_forget()
                    central.root.nametowidget('county.municipality').grid_forget()
            except KeyError as e:
                print("The issue is that the widget that you are looking for is not in the frame yet.")
                print(e)
                pass

            # if county selection isn't all, then populate the proper municipality data.
            if search.county.lower() != "all":
                municipalities = scrape.get_municipality(scrape.get_counties()[search.county])
                if municipalities is not None:
                    for widget in central.frame.winfo_children():
                        if 'row' in widget.grid_info() and widget.grid_info()['row'] > 0:
                            widget.grid(row=widget.grid_info()['row'] + 1, column=widget.grid_info()['column'])

                lbl_municipalities = Label(central.frame, name="lbl_municipalities", text="Municipalities: ")
                lbl_municipalities.grid(column=0, row=1, sticky='w')

                municipalities_lst = list(municipalities.keys())

                municipalities_lst.insert(0, "All")
                municipality_menu = ttk.Combobox(central.frame, values=municipalities_lst, name="municipality")
                municipality_menu.set(municipalities_lst[0])

                def post_municipalities():
                    search.update('municipality', municipality_menu.get())
                    if municipality_menu.get() != "ALL":
                        search.update('municipality_id', municipalities[municipality_menu.get()])
                    else:
                        search.update('municipality_id', None)


                municipality_menu.bind('<<ComboboxSelected>>', lambda _: post_municipalities())
                municipality_menu.grid(column=1, row=1)


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
            status = ttk.Combobox(central.frame, values=status_opt)
            status.set(status_opt[0])
            status.bind('<<ComboboxSelected>>', lambda _: search.update('status', status.get()))
            row = 1

            registered_opt = [e.name.replace("_", " ").title() for e in Registered]
            registered = ttk.Combobox(central.frame, values=registered_opt)
            registered.set(registered_opt[0])
            registered.bind('<<ComboboxSelected>>', lambda _: self.date_range(search, central, registered.get()))

            filer_opt = [e.name.title() for e in Filer]
            filer = ttk.Combobox(central.frame, values=filer_opt)
            filer.set(filer_opt[0])
            filer.bind('<<ComboboxSelected>>', lambda _: search.update('filer', filer.get()))

            status_label.grid(column=0, row=row, sticky='w')
            status.grid(column=1, row=row)
            row += 1

            filer_label.grid(column=0, row=row, sticky='w')
            filer.grid(column=1, row=row)
            row += 1

            registered_label.grid(column=0, row=row, sticky='w')
            registered.grid(column=1, row=row)
            row += 1

            submit_btn.grid(column=0, row=row, columnspan=2)
            row += 1
            advanced_btn.config(text="Hide Advanced Settings")
            advanced_btn.grid(column=0, row=row, columnspan=2)

            if search.county != "ALL":
                self.show_municipalities(central, search)

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

            self.date_from_lbl = Label(central.frame, text="Date From: ", name='lbl_date_from')
            self.date_to_lbl = Label(central.frame, text="Date To: ", name='lbl_date_to')

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
            try:
                central.root.nametowidget('county.lbl_date_from').grid_forget()
                central.root.nametowidget('county.lbl_date_to').grid_forget()

                # temporary solution
                for widget in central.frame.winfo_children():
                    if isinstance(widget, DateEntry):
                        widget.destroy()
            except KeyError as e:
                print(e)


def display_filers(search, central):
    filers = get_filers(search)
    filers = [Entity(filer, search) for filer in filers]
    for widget in central.frame.winfo_children():
        widget.destroy()

    frame = Frame(central.frame)
    frame.grid(row=2, column=0, sticky='nw')

    # Add a canvas in that frame
    canvas = Canvas(frame)
    canvas.grid(row=0, column=0, sticky="news")

    # Link a scrollbar to the canvas
    vsb = Scrollbar(frame, orient="vertical", command=canvas.yview)
    vsb.grid(row=0, column=1, sticky='ns')
    canvas.configure(yscrollcommand=vsb.set)

    # Create a frame to contain the buttons
    data = Frame(canvas)
    canvas.create_window((0, 0), window=data, anchor="nw")
    row = 0
    for filer in filers:
        cell = Frame(data, name=str(filer.id), borderwidth="2")
        cell.config(bd=1, relief=SOLID)
        c_name = Label(cell, text="Name: {0}".format(filer.name))
        c_name.grid(column=0, row=row, sticky='w')
        row += 1
        if search.filer == Filer.CANDIDATE:
            seat = Label(cell, text="Seat: {0}".format(filer.office))
            seat.grid(column=0, row=row, sticky='w')
            row += 1
        c_id = Label(cell, text="Filer ID: {0}".format(filer.id))
        c_registered = Label(cell, text="Registered: {0}".format(filer.registered))

        c_id.grid(column=0, row=row, sticky='w')
        row += 1
        c_registered.grid(column=0, row=row, sticky='w')
        central.root.bind("<Button-1>", get_candidate)
        cell.grid(column=0, row=row, sticky='news')
        row += 1

    data.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))






def get_candidate(event):
    if event.widget is not None:
        if str(event.widget).split(".")[-1] is not None:
            # print(str(event.widget.master).split(".")[-1])
            pass




st = Central()
st.root.mainloop()
