import React, { useState } from 'react';
import { TextField, Button, Container } from '@mui/material';
import axios from 'axios';

function App() {
  const [inputText, setInputText] = useState('');
  const [reversedText, setReversedText] = useState('');

  const handleSubmit = async () => {
    const response = await axios.post('http://localhost:3000/reverse', { text: inputText });
    setReversedText(response.data.reversed);
  };

  return (
    <Container maxWidth="sm">
      <TextField
        fullWidth
        label="Enter text"
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
        margin="normal"
      />
      <Button variant="contained" onClick={handleSubmit}>
        Reverse
      </Button>
      <TextField
        fullWidth
        label="Reversed text"
        value={reversedText}
        margin="normal"
        InputProps={{
          readOnly: true,
        }}
      />
    </Container>
  );
}

export default App;
