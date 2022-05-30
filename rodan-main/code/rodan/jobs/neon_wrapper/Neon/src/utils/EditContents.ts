/**
 * Contents of navbar menu after switching to edit mode.
 */
export const navbarDropdownMenu: HTMLDivElement = document.createElement('div');
navbarDropdownMenu.classList.add('navbar-item', 'has-dropdown', 'is-hoverable');
const fileLink = document.createElement('a');
fileLink.classList.add('navbar-link');
fileLink.textContent = 'File';
const navbarContents = document.createElement('div');
navbarContents.classList.add('navbar-dropdown');
navbarContents.id = 'navbar-dropdown-options';
const contents = [['save', 'Save'], ['export', 'Save and Export to File'],
  ['getmei', 'Download MEI'], ['revert', 'Revert']];
contents.forEach(content => {
  const item = document.createElement('a');
  item.id = content[0];
  item.classList.add('navbar-item');
  item.textContent = content[1];
  navbarContents.appendChild(item);
});
navbarDropdownMenu.appendChild(fileLink);
navbarDropdownMenu.appendChild(navbarContents);

/**
 * Finalize option in the navbar for rodan
 */
export const navbarFinalize =
    '<a id=\'finalize\' class=\'navbar-item\'> Finalize MEI </a>';

/**
 * Contents of the undo/redo panel with buttons
 */
export const undoRedoPanel: string =
    '<div class=\'field has-addons buttons\' style=\'overflow-x: auto;\'>' +
    '<p class=\'control\'>' +
    '<button class=\'button\' id=\'undo\'>Undo</button>' +
    '<button class=\'button\' id=\'redo\'>Redo</button></p></a></div>';
