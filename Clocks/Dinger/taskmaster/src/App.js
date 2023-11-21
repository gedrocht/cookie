// src/App.js
import React, { useState, useEffect } from 'react';
import { Button, TextField, List, ListItem, ListItemText, IconButton, Typography, Checkbox } from '@mui/material';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import DeleteIcon from '@mui/icons-material/Delete';
import axios from 'axios';
import { get_payday } from "./Payday.js"

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
  },
});

function App() {
  const [name, setName] = useState('');
  const [responseMessage, setResponseMessage] = useState('');
  const [reminders, setReminders] = useState([]);
  const [newReminder, setNewReminder] = useState('');
  const [currentTime, setCurrentTime] = useState(new Date());
  const [numShots, setNumShots] = useState(0);
  const [nextPayday, setNextPayday] = useState("Next paycheck will be");

  useEffect(() => {
    fetchValidReminders();
    fetchNumShots();
    setNextPayday(get_payday())
    const update_time_interval = setInterval(() => setCurrentTime(new Date()), 1000);
    const update_payday_interval = setInterval(() => setNextPayday(get_payday()), 600000); //600k seconds (10 minutes)
    // return () => clearInterval(interval); //???
  }, []);

  const fetchReminders = async () => {
    try {
      const response = await axios.get('http://192.168.0.133:5000/api/reminders');
      setReminders(response.data);
      console.log(response);
    } catch (error) {
      console.error('Error fetching reminders:', error);
    }
  };

  const fetchValidReminders = async () => {
    try {
      const response = await axios.get('http://192.168.0.133:5000/api/reminders/valid');
      setReminders(response.data);
      console.log(response);
    } catch (error) {
      console.error('Error fetching valid reminders:', error);
    }
  };

  const addReminder = async () => {
    try {
      await axios.post('http://192.168.0.133:5000/api/reminders', { reminder: newReminder });
      fetchValidReminders();
      setNewReminder('');
    } catch (error) {
      console.error('Error adding reminder:', error);
    }
  };

  const deleteReminder = async (id) => {
    try {
      await axios.delete('http://192.168.0.133:5000/api/reminders', { data: { id } });
      fetchValidReminders();
    } catch (error) {
      console.error('Error deleting reminder:', error);
    }
  };

  const completeReminder = async (ID) => {
    try {
      await axios.post('http://192.168.0.133:5000/api/reminders/complete', {ID});
      fetchValidReminders();
    } catch (error) {
      console.error("Error completing reminder:", error);
    }
  };

  const skipReminder = async (ID) => {
    try {
      await axios.post('http://192.168.0.133:5000/api/reminders/skip', {ID});
      fetchValidReminders();
    } catch (error) {
      console.error("Error completing reminder:", error);
    }
  };

  const addDelayReminder = async (ID) => {
    try {
      await axios.post('http://192.168.0.133:5000/api/reminders/add_delay', {ID});
      fetchValidReminders();
    } catch (error) {
      console.error("Error adding to reminder delay:", error);
    }
  };

  const subtractDelayReminder = async (ID) => {
    try {
      await axios.post('http://192.168.0.133:5000/api/reminders/subtract_delay', {ID});
      fetchValidReminders();
    } catch (error) {
      console.error("Error subtracting from reminder delay:", error);
    }
  };

  const sendMessage = async () => {
    try {
      const response = await axios.post('http://192.168.0.133:5000/api/message', { name });
      setResponseMessage(response.data.message);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const addShot = async () => {
    try {
      const response = await axios.post("http://192.168.0.133:5000/api/shots");
      fetchNumShots()
    } catch (error) {
      console.error("Error logging shot:", error);
    }
  }

  const fetchNumShots = async () => {
    try {
      const response = await axios.get('http://192.168.0.133:5000/api/shots');
      setNumShots(response.data);
      console.log(response);
    } catch (error) {
      console.error('Error fetching valid reminders:', error);
    }
  }

  const resetShots = async () => {
    try {
      const response = await axios.post("http://192.168.0.133:5000/api/shots/reset");
      fetchNumShots()
      console.log(response);
    } catch (error) {
      console.error("Error resetting shots taken:", error);
    }
  }

  return (
    <ThemeProvider theme={darkTheme}>
      <div style={{ margin: '20px' }}>
        <Typography style={{ marginBottom: "20px" }}>
          {nextPayday}
        </Typography>
        <span style={{display: "none"}}>
          <Typography variant="h5" style={{ marginBottom: '20px' }}>
            Current Time: {currentTime.toLocaleTimeString()}
          </Typography>
          <div>
            <input 
              type="text" 
              placeholder="Enter your name" 
              value={name} 
              onChange={e => setName(e.target.value)} 
            />
            <button onClick={sendMessage}>Send</button>
            {responseMessage && <p>{responseMessage}</p>}
          </div>

          <input 
            type="text" 
            value={newReminder} 
            onChange={(e) => setNewReminder(e.target.value)}
            style={{ marginRight: '10px' }}
          />
          <Button variant="contained" color="primary" onClick={addReminder}>
            Add Reminder
          </Button>
        </span>
        <Typography variant="h5" style={{ marginBottom: '20px' }}>
          {numShots} Shot{numShots===1?"":"s"} Taken
        </Typography>
        <Button style={{margin: '10px'}} variant="contained" color="primary" onClick={addShot}>
          Log Shot
        </Button>
        <Button style={{margin: '10px'}} variant="contained" color="secondary" onClick={resetShots}>
          Reset Shot Log
        </Button>
        <List>
          {reminders.map((reminder, index) => (
            <ListItem key={index} style={
              {
                borderBottom: "1px solid #ddd", 
                marginTop: '10px', 
                display: (reminder.SKIPPED === "True" || reminder.COMPLETED === "True") ? "none" : "block"
              }}>
              <ListItemText
                primary={<Typography>{reminder.reminder}</Typography>}
                secondary={<Typography>{new Date(0, 0, 0, parseInt(reminder.hour) + parseInt(reminder.DELAY), reminder.minute)
                  .toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })}</Typography>}
              />
              <Typography style={{display: reminder.DELAY === 0 ? "none" : ""}}>(Delayed by {reminder.DELAY} hour{reminder.DELAY===1?"":"s"})</Typography>
              <Button key={`${index}-CompleteButton`} style={{margin: '10px'}} variant="contained" color="primary" onClick={()=>{completeReminder(reminder.ID)}}>Complete</Button>
              <Button key={`${index}-SkipButton`} style={{margin: '10px'}} variant="contained" color="secondary" onClick={()=>{skipReminder(reminder.ID)}}>Skip</Button>
              <Button key={`${index}-AddDelayButton`} style={{margin: '10px'}} variant="contained" color="primary" onClick={()=>{addDelayReminder(reminder.ID)}}>Add Delay</Button>
              <Button disabled={reminder.delay > 0} key={`${index}-SubtractDelayButton`} style={{margin: '10px'}} variant="contained" color="secondary" onClick={()=>{subtractDelayReminder(reminder.ID)}}>Subtract Delay</Button>
            </ListItem>
          ))}
        </List>
        </div>
    </ThemeProvider>
  );
}

/*Object.entries(reminder).map(([key, value]) => (
  <Typography key={`${index}-${key}`}>{`${key}: ${value}`}</Typography>))}
*/

export default App;
