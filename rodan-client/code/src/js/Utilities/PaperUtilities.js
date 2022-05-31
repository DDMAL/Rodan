/**
 * Draws a grid on the current viewport
 * - If grid already exists, it removes and redraws it
 *
 * @param  {Number} cellSize - Size of each cell in pixels
 *
 * Author:
 * - Nicholas Kyriakides(@nicholaswmin, nik.kyriakides@gmail.com)
 *
 * License:
 * - MIT
 */
export function drawGrid(options, paperScope) 
{
    'use strict';
    this.cellSize = options.DIMENSION;
    this.gridColor = options.LINE_COLOR;
    this.lineWidth = options.LINE_WIDTH;
 
    var self = this;
    this.gridGroup;
 
    var boundingRect = paperScope.view.bounds;
    var rectanglesX = paperScope.view.bounds.width / this.cellSize;
    var rectanglesY = paperScope.view.bounds.height / this.cellSize;
 
    this.createGrid = function() {
 
        self.gridGroup = new paperScope.Group();
 
        //Vertical Lines
        for (var i = 0; i <= rectanglesX; i++) {
            var correctedLeftBounds = Math.ceil(boundingRect.left / self.cellSize) * self.cellSize;
            var xPos = correctedLeftBounds + i * self.cellSize;
            var topPoint = new paperScope.Point(xPos, boundingRect.top);
            var bottomPoint = new paperScope.Point(xPos, boundingRect.bottom);
            var gridLine = new paperScope.Path.Line(topPoint, bottomPoint);
            gridLine.strokeColor = self.gridColor;
            gridLine.strokeWidth = self.lineWidth / paperScope.view.zoom;
 
            self.gridGroup.addChild(gridLine);
 
        }
 
        //Horizontal Lines
        for (var i = 0; i <= rectanglesY; i++) {
            var correctedTopBounds = Math.ceil(boundingRect.top / self.cellSize) * self.cellSize;
            var yPos = correctedTopBounds + i * self.cellSize;
            var leftPoint = new paperScope.Point(boundingRect.left, yPos);
            var rightPoint = new paperScope.Point(boundingRect.right, yPos);
            var gridLine = new paperScope.Path.Line(leftPoint, rightPoint);
 
            gridLine.strokeColor = self.gridColor;
            gridLine.strokeWidth = self.lineWidth / paperScope.view.zoom;
 
            self.gridGroup.addChild(gridLine);
        }
 
        self.gridGroup.sendToBack();
        paperScope.view.update();
    }
 
    //Removes the children of the gridGroup and discards the gridGroup itself
    this.removeGrid = function() {
        for (var i = 0; i <= gridGroup.children.length-1; i++) {
          self.gridGroup.children[i].remove();
        }
        self.gridGroup.remove();
    }
 
    //Initialization
    if(typeof gridGroup === 'undefined') {
        this.createGrid();
    } else {
        this.removeGrid();
        this.createGrid();
    }
}