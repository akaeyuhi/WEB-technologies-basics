class ColorTable {
  _cols = 6;
  _rows = 6;
  _variantNumber = 5;
  _table = null;
  _colorPicker = null;

  constructor(table, picker) {
    this._table = table;
    this._colorPicker = picker;
    this.init();
  }

  get _randomColor() {
    const red = this._getRandomNumber(256);
    const green = this._getRandomNumber(256);
    const blue = this._getRandomNumber(256);
    return `rgb(${red},${green},${blue})`;
  }

  _generateCells() {
    let counter = 1;

    for (let i = 0; i < this._rows; i++) {
      const row = document.createElement('tr');

      for (let j = 0; j < this._cols; j++) {
        const col = document.createElement('td');
        col.dataset['id'] = counter;
        col.textContent = counter;
        row.appendChild(col);
        counter++;
      }
      this._table.appendChild(row);
    }
  }

  _getRandomNumber(max) {
    return Math.floor(Math.random() * max);
  }

  _cellMouseOverHandler(event) {
    event.target.style.backgroundColor = this._randomColor;
  }

  _сellClickHanlder(event) {
    event.target.style.backgroundColor = this._colorPicker.value;
  }

  _dbClickHandler(variantCell) {
    const cells = this._table.querySelectorAll('td');
    const color = this._colorPicker.value;
    const clickedCellId = Number(variantCell);

    cells.forEach((cell) => {
      const cellNumber = Number(cell.dataset['id']);
      if (cellNumber != clickedCellId) cell.style.backgroundColor = color;
    });
  }

  init() {
    this._generateCells();

    const variantCell = this._table.querySelector(
      `td[data-id="${this._variantNumber}"]`
    );

    variantCell.addEventListener('dblclick', () => {
      this._dbClickHandler(variantCell);
    });

    variantCell.addEventListener('click', (event) => {
      this._сellClickHanlder(event);
    });

    variantCell.addEventListener('mouseover', (event) =>
      this._cellMouseOverHandler(event)
    );
  }
}
