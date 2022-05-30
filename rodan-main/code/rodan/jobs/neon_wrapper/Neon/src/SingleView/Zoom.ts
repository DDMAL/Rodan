import * as d3 from 'd3';

export class ViewBox {
  a: number;
  b: number;
  c: number;
  d: number;

  imageHeight: number;
  imageWidth: number;

  /**
   * @param imageWidth - Width of the contained image.
   * @param imageHeight - Height of the contained image.
   */
  constructor (imageWidth: number, imageHeight: number) {
    this.a = 0;
    this.b = 0;
    this.c = imageWidth;
    this.d = imageHeight;

    this.imageWidth = imageWidth;
    this.imageHeight = imageHeight;
  }

  /**
   * Set values of the viewBox manually.
   * @param w - First value.
   * @param x - Second value.
   * @param y - Third value.
   * @param z - Fourth value.
   */
  set (w: number, x: number, y: number, z: number): void {
    this.a = w;
    this.b = x;
    this.c = y;
    this.d = z;
  }

  /** @returns Value for the viewBox parameter. */
  get (): string {
    return this.a.toString() + ' ' + this.b.toString() + ' ' +
      this.c + ' ' + this.d;
  }

  /** @param k - Factor to zoom to. */
  zoomTo (k: number): void {
    const zoomHeight = (this.imageHeight / k);
    const zoomWidth = (this.imageWidth / k);

    this.c = zoomWidth;
    this.d = zoomHeight;
  }

  /** @returns Current zoom factor. */
  getZoom (): number {
    return this.imageWidth / this.c;
  }

  /**
   * Translate viewport.
   * @param xDiff - Amount to shift on x-axis.
   * @param yDiff - Amount to shift on y-axis.
   */
  translate (xDiff: number, yDiff: number): void {
    this.a += xDiff;
    this.b += yDiff;
  }
}

export class ZoomHandler {
  dragCoordinates: DOMPoint;
  viewBox: ViewBox;
  matrix: DOMMatrix;

  /**
   * Reset the zoom and pan of the SVG viewbox
   */
  resetZoomAndPan (): void {
    const bgimg = document.getElementById('bgimg') as HTMLImageElement;
    this.viewBox = new ViewBox(parseInt(bgimg.getAttribute('width')), parseInt(bgimg.getAttribute('height')));

    this.updateViewBox();
  }

  /**
   * @param k - Factor to zoom to.
   */
  zoomTo (k: number): void {
    this.getViewBox();
    this.viewBox.zoomTo(k);
    this.updateViewBox();
  }

  /**
   * Translate the view box by relative coordinates.
  * @param xDiff - Amount to shift on x-axis.
  * @param yDiff - Amount to shift on y-axis.
  */
  translate (xDiff: number, yDiff: number): void {
    this.getViewBox();
    this.viewBox.translate(xDiff, yDiff);
    this.updateViewBox();
  }

  /**
   * Restore the view box to its position before the editor action.
   */
  restoreTransformation (): void {
    if (this.viewBox === undefined) {
      this.resetZoomAndPan();
    } else {
      this.updateViewBox();
    }
  }

  /**
   * Get the view box from the SVG in the page.
   */
  getViewBox (): void {
    if (this.viewBox === undefined) {
      const bgimg = document.getElementById('bgimg') as HTMLImageElement;
      this.viewBox = new ViewBox(parseInt(bgimg.getAttribute('width')), parseInt(bgimg.getAttribute('height')));
    }
    const rawViewBox = document.getElementById('svg_group')
      .getAttribute('viewBox')
      .split(' ');
    this.viewBox.set(
      parseInt(rawViewBox[0]),
      parseInt(rawViewBox[1]),
      parseInt(rawViewBox[2]),
      parseInt(rawViewBox[3])
    );
  }

  /**
   * Update the viewBox attribute of svg_group
   */
  updateViewBox (): void {
    document.getElementById('svg_group').setAttribute('viewBox', this.viewBox.get());
  }

  startDrag (): void {
    const group = document.getElementById('svg_group') as unknown as SVGSVGElement;
    this.dragCoordinates = group.createSVGPoint();
    if (d3.event.type === 'touchstart') {
      // If drag is triggered by a touch event
      this.dragCoordinates.x = d3.event.touches[0].screenX;
      this.dragCoordinates.y = d3.event.touches[0].screenY;
    } else {
      // Otherwise triggered by a mouse click
      this.dragCoordinates.x = d3.event.x;
      this.dragCoordinates.y = d3.event.y;
    }

    this.matrix = group.getScreenCTM().inverse();
  }

  dragging (): void {
    const group = document.getElementById('svg_group') as unknown as SVGSVGElement;
    const newCoordinates = group.createSVGPoint();
    // Same kind of checking as in startDrag
    if (d3.event.type === 'touchmove') {
      newCoordinates.x = d3.event.touches[0].screenX;
      newCoordinates.y = d3.event.touches[0].screenY;
    } else if (d3.event.type === 'wheel' && d3.event.shiftKey === false) {
      if (this.matrix === undefined) {
        this.matrix = group.getScreenCTM().inverse();
      }
      if (this.dragCoordinates === undefined) {
        this.dragCoordinates = group.createSVGPoint();
      }
      this.dragCoordinates.x = d3.event.x;
      this.dragCoordinates.y = d3.event.y;
      newCoordinates.x = this.dragCoordinates.x - d3.event.deltaX;
      newCoordinates.y = this.dragCoordinates.y - d3.event.deltaY;
      d3.event.preventDefault();
    } else {
      newCoordinates.x = d3.event.x;
      newCoordinates.y = d3.event.y;
    }
    const newTransform = newCoordinates.matrixTransform(this.matrix);
    const dragTransform = this.dragCoordinates.matrixTransform(this.matrix);
    this.translate(-newTransform.x + dragTransform.x, -newTransform.y + dragTransform.y);
    this.dragCoordinates = newCoordinates;
  }

  scrollZoom (): void {
    if (d3.event.type !== 'wheel') return;
    if (!d3.event.shiftKey) {
      this.dragging();
      return;
    }
    const slider = document.getElementById('zoomSlider') as HTMLInputElement;
    this.getViewBox();
    const k = this.viewBox.getZoom();
    let newK = k - d3.event.deltaX / 100;
    if (newK < parseInt(slider.getAttribute('min')) / 100) newK = 0.25;
    if (newK > parseInt(slider.getAttribute('max')) / 100) newK = 4;
    this.zoomTo(newK);

    // Update zoom slider
    slider.value = (newK * 100).toString();
    (document.getElementById('zoomOutput') as HTMLOutputElement).value = String(Math.round(newK * 100));
  }
}

export { ZoomHandler as default };
