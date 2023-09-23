class UserDto {
  picture = '';
  cell = '';
  country = '';
  email = '';
  gender = '';
  coordinates = 0;

  constructor(inputData) {
    this.picture = inputData.picture;
    this.gender = inputData.gender;
    this.cell = inputData.cell;
    this.country = inputData.country;
    this.email = inputData.email;
    this.coordinates = inputData.coordinates;
  }
}
