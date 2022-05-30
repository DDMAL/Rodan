import { getStaffBBox, selectBBox, selectStaff } from './SelectTools';
import NeonView from '../NeonView';
import DragHandler from './DragHandler';

import * as d3 from 'd3';

/**
 * Resize a staff or a syllable text bounding box.
 * For staves, this also supports adjusting the rotate.
 */
type Point = { x: number; y: number; name: number };

/**
 * The points you can click and drag to resize
 */
const PointNames = {
  TopLeft: 0,
  Top: 1,
  TopRight: 2,
  Right: 3,
  BottomRight: 4,
  Bottom: 5,
  BottomLeft: 6,
  Left: 7
};

function GetPoints(ulx: number, uly: number, lrx: number, lry: number, rotate: number): Point[] {
  // Note that arc functions return an angle x in [-pi/2, pi/2].
  let points: Array<Point>;
  // ul is ulx, uly, lr is lrx, lry
  if (rotate >= 0) {
    points = [
      { x: ulx, y: uly, name: PointNames.TopLeft },
      { x: (ulx + lrx) / 2, y: uly + (lrx - ulx) / 2 * Math.sin(rotate), name: PointNames.Top },
      { x: lrx, y: uly + (lrx - ulx) * Math.sin(rotate), name: PointNames.TopRight },
      { x: lrx, y: (uly + lry + (lrx - ulx) * Math.sin(rotate)) / 2, name: PointNames.Right },
      { x: lrx, y: lry, name: PointNames.BottomRight },
      { x: (ulx + lrx) / 2, y: lry - (lrx - ulx) / 2 * Math.sin(rotate), name: PointNames.Bottom },
      { x: ulx, y: lry - (lrx - ulx) * Math.sin(rotate), name: PointNames.BottomLeft },
      { x: ulx, y: (uly + lry - (lrx - ulx) * Math.sin(rotate)) / 2, name: PointNames.Left }
    ];
  }
  // Not that
  else {
    const a = (lrx - ulx) * Math.tan(Math.abs(rotate));
    const b = lry - uly - a;
    points = [
      { x: ulx, y: uly + a, name: PointNames.TopLeft },
      { x: (ulx + lrx) / 2, y: uly + a / 2, name: PointNames.Top },
      { x: lrx, y: uly, name: PointNames.TopRight },
      { x: lrx, y: uly + b / 2, name: PointNames.Right },
      { x: lrx, y: uly + b, name: PointNames.BottomRight },
      { x: (ulx + lrx) / 2, y: lry - a / 2, name: PointNames.Bottom },
      { x: ulx, y: lry, name: PointNames.BottomLeft },
      { x: ulx, y: lry - b / 2, name: PointNames.Left }
    ];
  }
  return points;
}

export function resize (element: SVGGraphicsElement, neonView: NeonView, dragHandler: DragHandler): void {
  /**
   * The upper-left x-coordinate of the element.
   */
  let ulx: number;
  /**
   * The upper-left y-coordinate of the element.
   */
  let uly: number;
  /**
   * The lower-right x-coordinate of the element.
   */
  let lrx: number;
  /**
   * The lower-right y-coordinate of the element.
   */
  let lry: number;

  /**
   * The rotate of the rect in radians.
   */
  let rotate: number;

  let initialPoint: number[], initialUly: number, initialLry: number,
    initialY: number, initialRectY: number, polyLen: number, dy: number, initialRotate: number;

  drawInitialRect();
  /**
   * Draw the initial rectangle around the element
   * and add the listeners to support dragging to resize.
   */
  function drawInitialRect (): void {
    if (element === null) return;

    // if it's a boundingbox just get the coordinates
    if (element.classList.contains('syl')) {
      const rect = element.querySelector('.sylTextRect-display');
      if (rect === null) {
        console.warn('Tried to draw resize rect for a sylTextRect that doesn\'t exist (or isn\'t displaying)');
        return;
      }
      ulx = Number(rect.getAttribute('x'));
      uly = Number(rect.getAttribute('y'));
      lrx = +ulx + +rect.getAttribute('width');
      lry = +uly + +rect.getAttribute('height');

      rotate = 0;
    }

    // if it's a staff use the paths to get it's boundingbox
    if (element.classList.contains('staff')) {
      const bbox = getStaffBBox(element);
      ulx = bbox.ulx;
      uly = bbox.uly;
      lrx = bbox.lrx;
      lry = bbox.lry;

      const coordinates: number[] = element.querySelector('path')
        .getAttribute('d')
        .match(/\d+/g)
        .map(element => Number(element));
      rotate = Math.atan((coordinates[3] - coordinates[1]) /
        (coordinates[2] - coordinates[0]));
    }

    let whichPoint: string;

    const points = GetPoints(ulx, uly, lrx, lry, rotate);

    polyLen = points[2].x - points[0].x;

    const pointString = points.filter((_elem, index) => { return index % 2 === 0; })
      .map(elem => elem.x + ',' + elem.y)
      .join(' ');

    d3.select('#' + element.id).append('polygon')
      .attr('points', pointString)
      .attr('id', 'resizeRect')
      .attr('stroke', 'black')
      .attr('stroke-width', 10)
      .attr('fill', 'none')
      .style('cursor', 'move')
      .style('stroke-dasharray', '20 10');

    for (const pointName in PointNames) {
      const point: Point = points[PointNames[pointName]];
      d3.select(element.viewportElement).append('circle')
        .attr('cx', point.x)
        .attr('cy', point.y)
        .attr('r', 25)
        .attr('stroke', 'black')
        .attr('stroke-width', 4)
        .attr('fill', '#0099ff')
        .attr('class', 'resizePoint')
        .attr('id', 'p-' + pointName);
    }

    // do it as a loop instead of selectAll so that you can easily know which point was
    for (const name in PointNames) {
      d3.select('#p-' + name).filter('.resizePoint').call(
        d3.drag()
          .on('start', () => { resizeStart(name); })
          .on('drag', resizeDrag)
          .on('end', resizeEnd.bind(this)));
    }

    if (element.classList.contains('staff')) {
      let x = points[3].x;
      let y = points[3].y;
      const pointStringRight = (x + 100) + ',' + (y + 85) + ' ' +
        (x + 70) + ',' + (y + 50) + ' ' + (x + 100) + ',' + (y + 15) + ' ' + (x + 130) + ',' + (y + 50);
      x = points[7].x;
      y = points[7].y;
      const pointStringLeft = (x - 100) + ',' + (y - 15) + ' ' +
        (x - 130) + ',' + (y - 50) + ' ' + (x - 100) + ',' + (y - 85) + ' ' + (x - 70) + ',' + (y - 50);

      d3.select('#' + element.id).append('polygon')
        .attr('points', pointStringRight)
        .attr('id', 'rotateRight')
        .attr('stroke', 'black')
        .attr('stroke-width', 7)
        .attr('fill', '#0099ff')
        .attr('class', 'rotatePoint');

      d3.select('#' + element.id).append('polygon')
        .attr('points', pointStringLeft)
        .attr('id', 'rotateLeft')
        .attr('stroke', 'black')
        .attr('stroke-width', 7)
        .attr('fill', '#0099ff')
        .attr('class', 'rotatePoint');

      d3.select('#rotateLeft').call(
        d3.drag()
          .on('start', rotateStart)
          .on('drag', rotateDragLeft)
          .on('end', rotateEnd));

      d3.select('#rotateRight').call(
        d3.drag()
          .on('start', rotateStart)
          .on('drag', rotateDragRight)
          .on('end', rotateEnd));
    }

    function rotateStart (): void {
      const which = d3.event.sourceEvent.target.id;
      initialY = d3.mouse(this)[1];
      initialLry = lry;
      initialUly = uly;
      initialRectY = (which === 'rotateRight' ? lry : uly);
      initialRotate = rotate;
    }

    function rotateDragLeft (): void {
      const currentY = d3.mouse(this)[1];
      const temp = currentY - initialY;
      const tempRotate = initialRotate - Math.atan(temp / polyLen);
      if (tempRotate > -0.2 && tempRotate < 0.2) {
        dy = temp;
        uly = initialRectY + dy;
        rotate = tempRotate;
        if (rotate >= 0) {
          uly = dy + points.filter(point => point.name === PointNames.TopLeft)[0].y;
          lry = points.filter(point => point.name === PointNames.BottomRight)[0].y;
        } else {
          uly = points.filter(point => point.name === PointNames.TopRight)[0].y;
          lry = dy + points.filter(point => point.name === PointNames.BottomLeft)[0].y;
        }
      }
      redraw();
    }

    function rotateDragRight (): void {
      const currentY = d3.mouse(this)[1];
      const temp = currentY - initialY;
      const tempRotate = initialRotate + Math.atan(temp / polyLen);
      if (tempRotate > -0.2 && tempRotate < 0.2) {
        dy = temp;
        rotate = tempRotate;
        if (rotate >= 0 ) {
          lry = dy + points.filter(point => point.name === PointNames.BottomRight)[0].y;
          uly = points.filter(point => point.name === PointNames.TopLeft)[0].y;
        } else {
          uly = dy + points.filter(point => point.name === PointNames.TopRight)[0].y;
          lry = points.filter(point => point.name === PointNames.BottomLeft)[0].y;
        }
      }
      redraw();
    }

    function rotateEnd (): void {
      if (dy === undefined) {
        dy = 0;
      }
      const editorAction = {
        'action': 'resizeRotate',
        'param': {
          'elementId': element.id,
          'ulx': ulx,
          'uly': uly,
          'lrx': lrx,
          'lry': lry,
          'rotate': rotate * 180 / Math.PI
        }
      };
      neonView.edit(editorAction, neonView.view.getCurrentPageURI()).then(async (result) => {
        if (result) {
          await neonView.updateForCurrentPage();
        }
        element = document.getElementById(element.id) as unknown as SVGGraphicsElement;
        ulx = undefined;
        uly = undefined;
        lrx = undefined;
        lry = undefined;
        dy = undefined;
        drawInitialRect();
        if (element.classList.contains('syl')) {
          selectBBox(element.querySelector('.sylTextRect-display'), dragHandler, this);
        } else {
          selectStaff(element, dragHandler);
        }
      });
    }

    function resizeStart (name: string): void {
      whichPoint = name;
      const point = points.find(point => { return point.name === PointNames[name]; });
      initialPoint = [point.x, point.y];
      initialUly = uly;
      initialLry = lry;
    }

    function resizeDrag (): void {
      const currentPoint = d3.mouse(this);
      switch (PointNames[whichPoint]) {
        case PointNames.TopLeft:
          ulx = currentPoint[0];
          uly = currentPoint[1];
          break;
        case PointNames.Top:
          uly = currentPoint[1] - (lrx - ulx) * Math.tan(rotate) / 2;
          break;
        case PointNames.TopRight:
          lrx = currentPoint[0];
          uly = currentPoint[1] - (lrx - ulx) * Math.tan(rotate);
          break;
        case PointNames.Right:
          lrx = currentPoint[0];
          lry = initialLry + (currentPoint[0] - initialPoint[0]) * Math.tan(rotate);
          break;
        case PointNames.BottomRight:
          lrx = currentPoint[0];
          lry = currentPoint[1];
          break;
        case PointNames.Bottom:
          lry = currentPoint[1] + (lrx - ulx) * Math.tan(rotate) / 2;
          break;
        case PointNames.BottomLeft:
          ulx = currentPoint[0];
          lry = currentPoint[1] + (lrx - ulx) * Math.tan(rotate);
          break;
        case PointNames.Left:
          ulx = currentPoint[0];
          uly = initialUly + (currentPoint[0] - initialPoint[0]) * Math.tan(rotate);
          break;
        default:
          console.error('Something that wasn\'t a side of the rectangle was dragged. This shouldn\'t happen.');
      }
      redraw();
    }

    function resizeEnd (): void {
      const editorAction = {
        'action': 'resize',
        'param': {
          'elementId': element.id,
          'ulx': ulx,
          'uly': uly,
          'lrx': lrx,
          'lry': lry
        }
      };
      neonView.edit(editorAction, neonView.view.getCurrentPageURI()).then(async (result) => {
        if (result) {
          await neonView.updateForCurrentPage();
        }
        element = document.getElementById(element.id) as unknown as SVGGraphicsElement;
        ulx = undefined;
        uly = undefined;
        lrx = undefined;
        lry = undefined;
        d3.selectAll('.resizePoint').remove();
        d3.selectAll('#resizeRect').remove();
        d3.selectAll('.rotatePoint').remove();
        drawInitialRect();
        if (element.classList.contains('syl')) {
          selectBBox(element.querySelector('.sylTextRect-display'), dragHandler, this);
        } else {
          try {
            document.getElementById('moreEdit').innerHTML = '';
            document.getElementById('moreEdit').classList.add('is-invisible');
          } catch (e) {}
        }
      });
    }
  }

  /**
   * Redraw the rectangle with the new bounds
   */
  function redraw (): void {
    const points: Point[] = GetPoints(ulx, uly, lrx, lry, rotate);

    const pointString: string = points.filter((_elem, index) => { return index % 2 === 0; })
      .map(elem => elem.x + ',' + elem.y)
      .join(' ');

    d3.select('#resizeRect').attr('points', pointString);

    for (const pointName in PointNames) {
      const point: Point = points[PointNames[pointName]];
      d3.select('#p-' + pointName).filter('.resizePoint')
        .attr('cx', point.x)
        .attr('cy', point.y);
    }

    let x = points[3].x;
    let y = points[3].y;
    const pointStringRight = (x + 100) + ',' + (y + 85) + ' ' +
      (x + 70) + ',' + (y + 50) + ' ' + (x + 100) + ',' + (y + 15) + ' ' + (x + 130) + ',' + (y + 50);
    x = points[7].x;
    y = points[7].y;
    const pointStringLeft = (x - 100) + ',' + (y - 15) + ' ' +
      (x - 130) + ',' + (y - 50) + ' ' + (x - 100) + ',' + (y - 85) + ' ' + (x - 70) + ',' + (y - 50);

    d3.select('#rotateLeft').attr('points', pointStringLeft);
    d3.select('#rotateRight').attr('points', pointStringRight);
  }
}
