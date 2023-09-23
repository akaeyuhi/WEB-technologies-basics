class Validator {
  _form = null;
  _formOutput = null;
  _data = null;
  _validationErrors = [];
  _data = [];
  _validationRules = {
    credentials: new RegExp(
      /^[А-ЯҐЄІЇ]{1}[а-яґєії]+\s{1}([а-яґєіїА-ЯҐЄІЇ]{1}.){2}$/
    ),
    email: new RegExp(/^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/),
    faculty: new RegExp(/^[А-ЯҐЄІЇ]{4}$/),
    date: new RegExp(/^[1-9][0-9]{3}-[0-9]{2}-[0-9]{2}$/),
    address: new RegExp(/^(м|с|(смт))\.\s[а-яґєіїА-ЯҐЄІЇ]+$/),
  };

  constructor(form, output) {
    this._form = form;
    this._formOutput = output;
    this._form.addEventListener('submit', (event) =>
      this._submitHandler(event)
    );
  }

  _resetErrors(fields) {
    this._data = [];
    this._validationErrors = [];
    for (const field of fields) {
      const inputEl = this._form.querySelector(`[name='${field}']`);
      inputEl.classList.remove('input-invalid');
    }
  }

  _submitHandler(event) {
    event.preventDefault();
    this._validate();
    if (this._validationErrors.length !== 0) return;
    this._render();
  }

  _validate() {
    const formData = new FormData(this._form);

    this._resetErrors(formData.keys());
    this._resetOutput();

    for (const [key, value] of formData) {
      const isValueValid = this._validationRules[key].test(value.trim());
      if (!isValueValid) {
        const inputEl = this._form.querySelector(`[name='${key}']`);
        inputEl.classList.add('input-invalid');
        this._validationErrors.push({ name: key });
      } else {
        this._data[key] = value;
      }
    }
  }

  _render() {
    const markup = `
    <h2>Введені дані:</h2>
    <ul>
      <li>ПІБ: <span>${this._data.credentials}</span></li>
      <li>Факультет: <span>${this._data.faculty}</span></li>
      <li>Дата народження: <span>${this._data.date}</span></li>
      <li>Адреса: <span>${this._data.address}</span></li>
      <li>email: <span>${this._data.email}</span></li>
    </ul>
  `;
    this._formOutput.insertAdjacentHTML('afterbegin', markup);
  }
  _resetOutput() {
    this._formOutput.innerHTML = '';
  }
}
