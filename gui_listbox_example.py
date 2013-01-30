"""GUI list box example.

Usage::

    python gui_listbox_example.py

"""
import Tkinter


def get_list(event):
  """Read the listbox selection and put the result in an entry widget."""
  # Get selected line index
  index = listbox1.curselection()[0]

  # Get the line's text
  seltext = listbox1.get(index)

  print 'SELECTED', seltext


root = Tkinter.Tk()
root.title('Listbox Operations')

# Create the listbox (note that size is in characters)
listbox1 = Tkinter.Listbox(root, width=50, height=6)
listbox1.grid(row=0, column=0)

# Populate list
my_options = ['Do this', 'Analyze that']
for opt in my_options:
    listbox1.insert(Tkinter.END, opt)

# Create a vertical scrollbar to the right of the listbox
yscroll = Tkinter.Scrollbar(command=listbox1.yview, orient=Tkinter.VERTICAL)
yscroll.grid(row=0, column=1, sticky=Tkinter.N+Tkinter.S)
listbox1.configure(yscrollcommand=yscroll.set)

# Left mouse click on a list item to display selection
listbox1.bind('<ButtonRelease-1>', get_list)

root.mainloop()
