import { createContext, useContext, useEffect, useState, useRef } from 'react';
import { io } from 'socket.io-client';
import { useAuth } from './AuthContext';

const SocketContext = createContext(null);

const SOCKET_URL = 'http://localhost:8000';

export function SocketProvider({ children }) {
  const { user } = useAuth();
  const socketRef = useRef(null);
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [groups, setGroups] = useState([]);
  const [directMessages, setDirectMessages] = useState({});

  useEffect(() => {
    if (user?.user_id) {
      const socket = io(`${SOCKET_URL}/ws/${user.user_id}`, {
        transports: ['websocket'],
      });

      socket.on('connect', () => {
        setConnected(true);
      });

      socket.on('disconnect', () => {
        setConnected(false);
      });

      socket.on('new_message', (data) => {
        setMessages((prev) => [...prev, data]);
      });

      socket.on('group_message', (data) => {
        setGroups((prev) => [...prev, data]);
      });

      socket.on('dm_message', (data) => {
        setDirectMessages((prev) => {
          const key = `${data.sender_id}-${data.receiver_id}`;
          const existing = prev[key] || [];
          return { ...prev, [key]: [...existing, data] };
        });
      });

      socketRef.current = socket;

      return () => {
        socket.disconnect();
      };
    }
  }, [user?.user_id]);

  const sendMessage = (type, payload) => {
    if (socketRef.current) {
      socketRef.current.emit(type, payload);
    }
  };

  return (
    <SocketContext.Provider value={{ connected, messages, groups, directMessages, sendMessage }}>
      {children}
    </SocketContext.Provider>
  );
}

export function useSocket() {
  const context = useContext(SocketContext);
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
}