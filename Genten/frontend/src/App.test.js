// File: frontend/src/App.test.js
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';
import axios from 'axios';

// Mock the axios module
jest.mock('axios');

describe('App component interactions', () => {
  test('allows users to enter a model filename', () => {
    render(<App />);
    const input = screen.getByTestId('model-input');
    userEvent.type(input, 'new_model.obj');
    expect(input).toHaveValue('new_model.obj');
  });

  test('sends correct data when setting the model', async () => {
    axios.post.mockResolvedValue({ status: 200 });  // Mocking a successful POST request
    render(<App />);
    const input = screen.getByTestId('model-input');
    const button = screen.getByTestId('set-model-button');
    userEvent.type(input, 'new_model.obj');
    userEvent.click(button);

    await waitFor(() => expect(axios.post).toHaveBeenCalledWith('http://localhost:3001/api/model', { model: 'new_model.obj' }));
  });

  test('fetches and displays the model correctly', async () => {
    axios.get.mockResolvedValue({ data: 'current_model.obj' });  // Mocking a successful GET request
    render(<App />);
    const fetchButton = screen.getByTestId('fetch-model-button');
    userEvent.click(fetchButton);

    await waitFor(() => {
      expect(axios.get).toHaveBeenCalledWith('http://localhost:3001/api/model');
      expect(screen.getByTestId('current-model')).toHaveTextContent('current_model.obj');
    });
  });
});
