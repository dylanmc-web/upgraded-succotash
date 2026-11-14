from dataclasses import dataclass
from drafter import *

WEIGHT_CLASSES = ["106", "113", "120", "126", "132", "138", "144", "150",
                  "157", "165", "175", "190", "215", "285"]
ALL_SCHOOLS = "All Schools"

set_website_title("Mat Tracker")
@dataclass
class Wrestler:
    """One wrestler on the roster and their season record."""
    name: str
    school: str
    weight_class: int
    wins: int
    losses: int


@dataclass
class State:
    
    wrestlers: list[Wrestler]
    message: str
    editing_name: str
    school_filter: str



def win_percentage(wrestler: Wrestler) -> int:
    "Return the wrestler's win percentage"
    total_matches = wrestler.wins + wrestler.losses
    if total_matches == 0:
        return 0
    return round(wrestler.wins / total_matches * 100)


def wrestler_names(wrestlers: list[Wrestler]) -> list[str]:
    "Return a list of every wrestler's name."
    names = []
    for wrestler in wrestlers:
        names.append(wrestler.name)
    return names


def school_names(wrestlers: list[Wrestler]) -> list[str]:
    "Return each school on the roster once, in the order they were added."
    schools = []
    for wrestler in wrestlers:
        if wrestler.school not in schools:
            schools.append(wrestler.school)
    return schools


def check_input(name: str, school: str, wins: str, losses: str) -> str:
    if name == "" or school == "":
        return "Please enter a name and a school."
    if not wins.isdigit() or not losses.isdigit():
        return "Wins and losses must be whole numbers."
    return ""


def wrestler_form(name: str, school: str, weight_class: str, wins: str,
                  losses: str) -> list:
    """Return the input boxes for a wrestler, filled in with given values."""
    return [
        Text("Name:"),
        TextBox("name", name),
        Text("School:"),
        TextBox("school", school),
        Text("Weight class (lbs):"),
        SelectBox("weight_class", WEIGHT_CLASSES, weight_class),
        Text("Wins:"),
        TextBox("wins", wins),
        Text("Losses:"),
        TextBox("losses", losses),
    ]



@route
def index(state: State) -> Page:
    """Home page: welcome text and navigation buttons."""
    return Page(state, [
        Text("Keep track of high school wrestlers and their records."),
        Text("Wrestlers on the roster: " + str(len(state.wrestlers))),
        Button("Add a Wrestler", add_wrestler_page),
        Button("View Roster", view_roster),
        Button("Edit Roster", choose_wrestler_page),
    ])


@route
def add_wrestler_page(state: State) -> Page:
    """Form page for entering a new wrestler."""
    content = [Header("Add a Wrestler"), Text(state.message)]
    content = content + wrestler_form("", "", WEIGHT_CLASSES[0], "0", "0")
    content.append(Button("Add to Roster", add_wrestler))
    content.append(Button("Back Home", index))
    return Page(state, content)


@route
def add_wrestler(state: State, name: str, school: str, weight_class: str,
                 wins: str, losses: str) -> Page:
    """Check the form input and, if valid, add the wrestler to the roster."""
    error = check_input(name, school, wins, losses)
    if error != "":
        state.message = error
        return add_wrestler_page(state)
    new_wrestler = Wrestler(name, school, int(weight_class), int(wins),
                            int(losses))
    state.wrestlers.append(new_wrestler)
    state.message = "Added " + name + " to the roster!"
    return view_roster(state)


@route
def view_roster(state: State) -> Page:
    """Show the wrestlers from the chosen school and their stats."""
    school_choices = [ALL_SCHOOLS] + school_names(state.wrestlers)
    if state.school_filter not in school_choices:
        state.school_filter = ALL_SCHOOLS
    rows = []
    for wrestler in state.wrestlers:
        if (state.school_filter == ALL_SCHOOLS
                or wrestler.school == state.school_filter):
            record = str(wrestler.wins) + "-" + str(wrestler.losses)
            percent = str(win_percentage(wrestler)) + "%"
            rows.append([wrestler.name, wrestler.school,
                         str(wrestler.weight_class), record, percent])
    content = [
        Header("Roster"),
        Text(state.message),
        Text("Show school:"),
        SelectBox("school_filter", school_choices, state.school_filter),
        Button("Apply", apply_filter),
    ]
    if len(rows) > 0:
        content.append(Table(rows, header=["Name", "School", "Weight",
                                           "Record", "Win %"]))
    else:
        content.append(Text("No wrestlers yet."))
    content.append(Button("Add a Wrestler", add_wrestler_page))
    content.append(Button("Edit Roster", choose_wrestler_page))
    content.append(Button("Back Home", index))
    return Page(state, content)


@route
def apply_filter(state: State, school_filter: str) -> Page:
    """Save which school to show, then show the roster again."""
    state.school_filter = school_filter
    state.message = ""
    return view_roster(state)


@route
def choose_wrestler_page(state: State) -> Page:
    """Let the user pick which wrestler on the roster to edit."""
    if len(state.wrestlers) == 0:
        return Page(state, [
            Header("Edit Roster"),
            Text("Add a wrestler first."),
            Button("Back Home", index),
        ])
    names = wrestler_names(state.wrestlers)
    return Page(state, [
        Header("Edit Roster"),
        Text("Choose a wrestler:"),
        SelectBox("name", names, names[0]),
        Button("Edit", edit_wrestler_page),
        Button("Back Home", index),
    ])


@route
def edit_wrestler_page(state: State, name: str) -> Page:
    """Show the chosen wrestler's info in a form so it can be changed."""
    state.editing_name = name
    for wrestler in state.wrestlers:
        if wrestler.name == name:
            content = [Header("Editing " + name), Text(state.message)]
            content = content + wrestler_form(
                wrestler.name, wrestler.school, str(wrestler.weight_class),
                str(wrestler.wins), str(wrestler.losses))
            content.append(Button("Save Changes", save_wrestler))
            content.append(Button("Remove Wrestler", remove_wrestler))
            content.append(Button("Cancel", view_roster))
            return Page(state, content)
    state.message = "Could not find " + name + "."
    return view_roster(state)


@route
def save_wrestler(state: State, name: str, school: str, weight_class: str,
                  wins: str, losses: str) -> Page:
    """Replace the edited wrestler's info with the new form values."""
    error = check_input(name, school, wins, losses)
    if error != "":
        state.message = error
        return edit_wrestler_page(state, state.editing_name)
    for wrestler in state.wrestlers:
        if wrestler.name == state.editing_name:
            wrestler.name = name
            wrestler.school = school
            wrestler.weight_class = int(weight_class)
            wrestler.wins = int(wins)
            wrestler.losses = int(losses)
    state.message = "Saved changes to " + name + "."
    state.editing_name = ""
    return view_roster(state)


@route
def remove_wrestler(state: State, name: str, school: str, weight_class: str,
                    wins: str, losses: str) -> Page:
    """
    Remove the wrestler being edited from the roster.

    The form values are passed in because this button is on the edit form,
    but only state.editing_name is needed to know who to remove.
    """
    kept = []
    for wrestler in state.wrestlers:
        if wrestler.name != state.editing_name:
            kept.append(wrestler)
    state.wrestlers = kept
    state.message = "Removed " + state.editing_name + " from the roster."
    state.editing_name = ""
    return view_roster(state)



# Helper function tests
assert_equal(win_percentage(Wrestler("A", "Central", 120, 3, 1)), 75)
assert_equal(win_percentage(Wrestler("A", "Central", 120, 0, 0)), 0)
assert_equal(wrestler_names([Wrestler("Ava", "Central", 120, 1, 0),
                             Wrestler("Ben", "North", 150, 0, 1)]),
             ["Ava", "Ben"])
assert_equal(school_names([Wrestler("Ava", "Central", 120, 1, 0),
                           Wrestler("Ben", "North", 150, 0, 1),
                           Wrestler("Cal", "Central", 132, 2, 2)]),
             ["Central", "North"])
assert_equal(check_input("", "Central", "1", "1"),
             "Please enter a name and a school.")
assert_equal(check_input("Ava", "Central", "ten", "1"),
             "Wins and losses must be whole numbers.")
assert_equal(check_input("Ava", "Central", "10", "1"), "")

# index
assert_equal(
    index(State([], "", "", ALL_SCHOOLS)),
    Page(State([], "", "", ALL_SCHOOLS), [
        Text("Keep track of high school wrestlers and their records."),
        Text("Wrestlers on the roster: 0"),
        Button("Add a Wrestler", add_wrestler_page),
        Button("View Roster", view_roster),
        Button("Edit Roster", choose_wrestler_page),
    ]))

# add_wrestler_page
assert_equal(add_wrestler_page(State([], "", "", ALL_SCHOOLS)).content[0],
             Header("Add a Wrestler"))

# add_wrestler: valid input adds the wrestler
assert_equal(
    add_wrestler(State([], "", "", ALL_SCHOOLS),
                 "Ava", "Central", "120", "10", "2").state,
    State([Wrestler("Ava", "Central", 120, 10, 2)],
          "Added Ava to the roster!", "", ALL_SCHOOLS))
# add_wrestler: missing name shows an error and adds nobody
assert_equal(
    add_wrestler(State([], "", "", ALL_SCHOOLS),
                 "", "Central", "120", "10", "2").state,
    State([], "Please enter a name and a school.", "", ALL_SCHOOLS))

# view_roster: empty roster
assert_equal(view_roster(State([], "", "", ALL_SCHOOLS)).content[5],
             Text("No wrestlers yet."))
# view_roster: only shows wrestlers from the chosen school
assert_equal(
    view_roster(State([Wrestler("Ava", "Central", 120, 10, 2),
                       Wrestler("Ben", "North", 150, 5, 5)],
                      "", "", "North")).content[5],
    Table([["Ben", "North", "150", "5-5", "50%"]],
          header=["Name", "School", "Weight", "Record", "Win %"]))

# apply_filter: saves the chosen school
assert_equal(
    apply_filter(State([Wrestler("Ben", "North", 150, 5, 5)],
                       "", "", ALL_SCHOOLS), "North").state,
    State([Wrestler("Ben", "North", 150, 5, 5)], "", "", "North"))

# choose_wrestler_page
assert_equal(choose_wrestler_page(State([], "", "", ALL_SCHOOLS)).content[1],
             Text("Add a wrestler first."))

# edit_wrestler_page: remembers who is being edited
assert_equal(
    edit_wrestler_page(State([Wrestler("Ava", "Central", 120, 10, 2)],
                             "", "", ALL_SCHOOLS), "Ava").state.editing_name,
    "Ava")

# save_wrestler: changes the wrestler's info
assert_equal(
    save_wrestler(State([Wrestler("Ava", "Central", 120, 10, 2)],
                        "", "Ava", ALL_SCHOOLS),
                  "Ava", "Central", "126", "12", "3").state,
    State([Wrestler("Ava", "Central", 126, 12, 3)],
          "Saved changes to Ava.", "", ALL_SCHOOLS))

# remove_wrestler: takes the wrestler off the roster
assert_equal(
    remove_wrestler(State([Wrestler("Ava", "Central", 120, 10, 2),
                           Wrestler("Ben", "North", 150, 5, 5)],
                          "", "Ava", ALL_SCHOOLS),
                    "Ava", "Central", "120", "10", "2").state,
    State([Wrestler("Ben", "North", 150, 5, 5)],
          "Removed Ava from the roster.", "", ALL_SCHOOLS))



set_site_information(
    author="Your Name Here",
    description="A roster and stat tracker for high school wrestlers.",
    sources=["Drafter documentation"],
    planning=["planning_document.pdf"],
    links=["https://github.com/YOUR-USERNAME/YOUR-REPO"]
)
hide_debug_information()
start_server(State([], "", "", ALL_SCHOOLS))
