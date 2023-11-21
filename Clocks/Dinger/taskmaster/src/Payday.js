  const get_month_days = (month_id, leap_year = false) => {
      switch(month_id) {
          case 3:
          case 5:
          case 10:
          case 8:
              return 30;
          case 1:
              return leap_year ? 29 : 28;
          default:
              return 31;
      }
  };

  const is_weekend = (month_id, date, year) => {
      let date_object = new Date(year, month_id, date);
      console.log(`is_weekend(${month_id}, ${date}, ${year})`);
      console.log("\t" + date_object)
      console.log(`\t-> ${date_object.getDay() === 0 || date_object.getDay() === 6}`)
      return date_object.getDay() === 0 || date_object.getDay() === 6;
  }

  const is_leap_year = (year) => {
      return year % 4 === 0;
  }

  const get_previous_month = (month_id) => {
      let result = month_id - 1;
      if (result < 0) {
          console.log(`get_previous_month(${month_id}) -> 11`)
          return 11;
      }
      console.log(`get_previous_month(${month_id}) -> ${result}`)
      return result;
  }

  const get_previous_day = (starting_month_id, starting_date, starting_year) => {
      let previous_month_id = starting_month_id;
      let previous_date = starting_date - 1;
      let previous_year = starting_year;

      if (previous_date < 0) {
          previous_month_id = get_previous_month(previous_month_id);
          if (previous_month_id === 11) {
              previous_year--;
          }
          previous_date = get_month_days(previous_month_id, previous_year);
      }
      console.log(`get_previous_day(${starting_month_id}, ${starting_date}, ${starting_year}) -> [${previous_month_id}, ${previous_date}, ${previous_year}]`);
      return [previous_month_id, previous_date, previous_year];
  }

  const get_expected_pay_date = (official_month_id, official_date, official_year) => {
      let expected_month_id = official_month_id;
      let expected_date = official_date;
      let expected_year = official_year;

      while (is_weekend(expected_month_id, expected_date, expected_year)) {
          let previous_day = get_previous_day(expected_month_id, expected_date, expected_year);
          expected_month_id = previous_day[0];
          expected_date = previous_day[1];
          expected_year = previous_day[2];
      }

      for(let i = 0 ; i < 1 ; i++) {
          let previous_day = get_previous_day(expected_month_id, expected_date, expected_year);
          expected_month_id = previous_day[0];
          expected_date = previous_day[1];
          expected_year = previous_day[2];
      }

      while (is_weekend(expected_month_id, expected_date, expected_year)) {
          let previous_day = get_previous_day(expected_month_id, expected_date, expected_year);
          expected_month_id = previous_day[0];
          expected_date = previous_day[1];
          expected_year = previous_day[2];
      }

      console.log(`get_expected_pay_date(${official_month_id}, ${official_date}, ${official_year}) -> [${expected_month_id}, ${expected_date}, ${expected_year}]`);
      return [expected_month_id, expected_date, expected_year];
  };

  const get_next_pay_date = () => {
      let current_month_id = -999;
      let current_date = -999;
      let current_year = -999;

      if (current_month_id === -999 &&
          current_date === -999 &&
          current_year === -999) {
              let today = new Date();
              current_month_id = today.getMonth();
              current_date = today.getDate();
              current_year = today.getFullYear();
      }
      let official_month_id = current_month_id;
      let official_date = 123;
      let official_year = current_year;

      if (current_date < 7) {
          official_date = 7;
      } else if (current_date < 22) {
          official_date = 22;
      } else {
          if (official_month_id === 11) {
              official_month_id = 0;
              official_year++;
          } else {
              official_month_id++;
          }
          official_date = 7;
      }

      // console.log(`get_next_pay_date(${current_month_id}, ${current_date}, ${current_year}) -> get_expected_pay_date(${official_month_id}, ${official_date}, ${official_year})`);
      return get_expected_pay_date(official_month_id, official_date, official_year);
  }

export const get_payday = () => {
  let payday = get_next_pay_date();
  let payday_date_object = new Date(payday[2], payday[0], payday[1]);
  let num_days = Math.ceil((payday_date_object - new Date()) / (1000*60*60*24));

  if (num_days === 0) {
    return "Next paycheck is today";
  } else if (num_days < 0) {
    if (num_days === -1) {
        return "Next paycheck was yesterday";
    } else {
        return `Next paycheck was ${num_days} ago`;
    }
  }
  return `Next paycheck in ${num_days} day${num_days===1?"":"s"} on ${payday_date_object.toDateString()}`;
}