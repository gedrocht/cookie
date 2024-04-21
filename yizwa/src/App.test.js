import { render, screen, fireEvent } from '@testing-library/react';
import App from './App';
import axios from 'axios';

jest.mock('axios');

it('submits text and displays reversed text', async () => {
  axios.post.mockResolvedValue({ data: { reversed: 'olleh' } });
  render(<App />);
  fireEvent.change(screen.getByLabelText(/enter text/i), { target: { value: 'hello' } });
  fireEvent.click(screen.getByRole('button', { name: /reverse/i }));
  const reversedText = await screen.findByDisplayValue('olleh');
  expect(reversedText).toBeInTheDocument();
});
