function getRandomPokemon() {
  let randomIndex = Math.random() * (pokemon.length-1);
  randomIndex = Math.round(randomIndex);
  return pokemon[randomIndex];
}

function getRandomPokemon() {
  return pokemon[Math.round(Math.random()*(pokemon.length-1))];
}

function choose(arr) {
  return arr[Math.round(Math.random()*(arr.length-1))];
}