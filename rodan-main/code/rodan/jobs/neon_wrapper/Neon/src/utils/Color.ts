/**
 * Adapted from color palette from Figure 2 (Colors optimized for color-blind
 * individuals) from
 * ["Points of view: Color blindness" by Bang Wong published in Nature Methods volume 8 on 27 May 2011](https://www.nature.com/articles/nmeth.1618?WT.ec_id=NMETH-201106)
 */
const ColorPalette: string[] = [
  'rgb(230, 159, 0)',
  'rgb(86, 180, 233)',
  'rgb(0, 158, 115)',
  'rgb(240, 228, 66)',
  'rgb(0, 114, 178)',
  'rgb(213, 94, 0)',
  'rgb(204, 121, 167)'
];

/**
 * Remove the highlight from a staff.
 * @param staff If undefined, the all staves are unhighlighted.
 */
export function unhighlight (staff?: SVGGElement): void {
  let children: NodeListOf<Element>;
  if (staff) {
    children = staff.querySelectorAll(':not(.selected) .highlighted');
  } else {
    children = document.querySelectorAll(':not(.selected) .highlighted');
  }
  children.forEach(elem => {
    if (elem.tagName === 'path' && !elem.closest('.staff').classList.contains('selected')) {
      elem.setAttribute('stroke', '#000000');
    } else {
      elem.removeAttribute('fill');
      let rects = elem.querySelectorAll('.sylTextRect-display');
      if (!rects.length) {
        try {
          rects = elem.closest('.syllable').querySelectorAll('.sylTextRect-display');
        } catch (e) {
          rects = [] as unknown as NodeListOf<Element>;
        }
      }
      rects.forEach(function (rect: HTMLElement) {
        if (rect.closest('.syllable').classList.contains('selected') ||
            rect.closest('.staff').classList.contains('selected') ||
            rect.closest('.syl').classList.contains('selected')) {
          rect.style.fill = 'red';
        } else {
          rect.style.fill = 'blue';
        }
        rect.classList.remove('highlighted');
      });
    }
    elem.classList.remove('highlighted');
  });
}

/**
 * Remove the highlight from each staff.
 */
export function unsetStaffHighlight (): void {
  unhighlight();
}

/**
 * Unset highlight for all grouping types
 */
export function unsetGroupingHighlight (): void {
  unsetStaffHighlight();
  const highlighted = Array.from(document.getElementsByClassName('highlighted'))
    .filter((elem: HTMLElement) => !elem.parentElement.classList.contains('selected'));
  highlighted.forEach((elem: HTMLElement) => {
    elem.setAttribute('fill', null);
    let rects = elem.querySelectorAll('.sylTextRect-display');
    if (!rects.length) {
      if (elem.closest('.syllable') !== null) {
        rects = elem.closest('.syllable').querySelectorAll('sylTextRect-display');
      }
    }
    rects.forEach(function (rect: HTMLElement) {
      if (rect.closest('.syllable').classList.contains('selected') || rect.closest('.syl').classList.contains('selected')) {
        rect.style.fill = 'red';
      } else {
        rect.style.fill = 'blue';
      }
      rect.classList.remove('highlighted');
    });
    elem.classList.remove('highlighted');
    elem.querySelectorAll('sylTextRect-display').forEach(rect => {
      rect.classList.remove('highlighted');
    });
  });
  Array.from(document.getElementsByClassName('selected')).forEach((el) => {el.setAttribute('fill', '');});
}

/**
 * Highlight a staff a certain color.
 */
export function highlight (staff: SVGGElement, color: string): void {
  const children = Array.from(staff.children);
  for (let i = 0; i < children.length; i++) {
    const child = children[i];
    if (child.tagName === 'path') {
      child.setAttribute('stroke', color);
    } else if (child.classList.contains('resizePoint') || child.id === 'resizeRect' || child.classList.contains('rotatePoint')) {
      return;
    } else if (child.classList.contains('layer')) {
      Array.from(child.children).forEach(cchild => { children.push(cchild); });
    } else if (document.getElementsByClassName('highlight-selected').length &&
      document.getElementsByClassName('highlight-selected')[0].id === 'highlight-neume'
      && child.classList.contains('syllable')) {
      Array.from(child.children).filter(el => el.classList.contains('neume')).forEach(cchild => { children.push(cchild); });
    } else {
      child.setAttribute('fill', color);
      let rects = child.querySelectorAll('.sylTextRect-display');
      if (!rects.length) {
        try {
          rects = child.closest('.syllable').querySelectorAll('.sylTextRect-display');
        } catch (e) {
          rects = [] as unknown as NodeListOf<Element>;
        }
      }
      rects.forEach(function (rect: HTMLElement) {
        if (!(rect.closest('.syllable').classList.contains('selected') ||
              rect.closest('.syl').classList.contains('selected') ||
              rect.closest('.staff').classList.contains('selected'))) {
          rect.style.fill = color;
          rect.classList.add('highlighted');
        }
      });
    }
    child.classList.add('highlighted');
  }
  let width, height;
  /*try {
    width = Number(document.querySelector('.active-page').querySelector('svg').getAttribute('width').split('px')[0]);
    height = Number(document.querySelector('.active-page').querySelector('svg').getAttribute('height').split('px')[0]);
  } catch (e) {
    console.debug(e);
  }*/
  let stroke: string;
  if (width !== undefined && height !== undefined) {
    // idk looks good :')
    // TODO find a better way of calculating this as this actually doesn't work as well as 30px
    stroke = (width*height/1000000).toString();
  }
  else {
    stroke = '30px';
  }
  staff.querySelectorAll('.nc, .custos, .clef').forEach(el => {
    el.setAttribute('stroke', 'black');
    el.setAttribute('stroke-width', stroke);
  });
}

/**
 * Highlight each staff a different color.
 */
export function setStaffHighlight (): void {
  const staves = Array.from(document.getElementsByClassName('staff')) as SVGGElement[];
  for (let i = 0; i < staves.length; i++) {
    const staffColor = ColorPalette[i % ColorPalette.length];
    highlight(staves[i], staffColor);
  }
}

/**
 * Set a highlight by a different grouping.
 * @param grouping - Either "staff", "syllable", or "neume".
 */
export function setGroupingHighlight (grouping: string): void {
  unsetGroupingHighlight();
  if (grouping === 'staff') {
    setStaffHighlight();
    return;
  } else if (grouping === 'selection') {
    const temp = document.querySelector('.sel-by.is-active').id;
    switch (temp) {
      case 'selBySyl':
      case 'selByBBox':
        grouping = 'syllable';
        break;
      case 'selByStaff':
        grouping = 'staff';
        break;
      default:
        grouping = 'neume';
        break;
    }
    setGroupingHighlight(grouping);
    return;
  }

  const groups = document.getElementsByClassName(grouping) as HTMLCollectionOf<HTMLElement>;
  for (let i = 0; i < groups.length; i++) {
    const groupColor = ColorPalette[i % ColorPalette.length];
    if ((groups[i].closest('.selected') === null) && !groups[i].classList.contains('selected')) {
      groups[i].setAttribute('fill', groupColor);
      const rects = groups[i].querySelectorAll('.sylTextRect-display') as NodeListOf<HTMLElement>;
      rects.forEach(function (rect) {
        if (rect.closest('.syl').classList.contains('selected') ||
            rect.closest('.syllable').classList.contains('selected') ||
            rect.closest('.staff').classList.contains('selected')) {
          return;
        }
        rect.style.fill = groupColor;
      });
      groups[i].classList.add('highlighted');
      groups[i].querySelectorAll('.sylTextRect-display').forEach(rect => {
        rect.classList.add('highlighted');
      });
    } else {
      if (!groups[i].classList.contains('selected')) {
        groups[i].setAttribute('fill', null);
      } else {
        groups[i].setAttribute('fill', '#d00');
      }
      groups[i].classList.remove('highlighted');
    }
  }
  document.querySelectorAll('.nc, .custos, .clef').forEach(el => {
    el.setAttribute('stroke', 'black');
    el.setAttribute('stroke-width', '30px');
  });
}
