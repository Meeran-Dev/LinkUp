const API_URL = 'http://127.0.0.1:8000';

export const api = {
  async register(username, email, password) {
    const res = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Registration failed');
    }
    return res.json();
  },

  async login(username, password) {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Login failed');
    }
    return res.json();
  },

  async getUser(token) {
    const res = await fetch(`${API_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to get user');
    return res.json();
  },

  async getDirectMessages(senderId, receiverId, token) {
    const res = await fetch(`${API_URL}/dm/messages?sender_id=${senderId}&receiver_id=${receiverId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to get messages');
    return res.json();
  },

  async sendDirectMessage(senderId, receiverId, content, token) {
    const res = await fetch(`${API_URL}/dm/send`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}` 
      },
      body: JSON.stringify({ sender_id: senderId, receiver_id: receiverId, content }),
    });
    if (!res.ok) throw new Error('Failed to send message');
    return res.json();
  },

  async getGroups(userId, token) {
    const res = await fetch(`${API_URL}/groups/list?user_id=${userId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to get groups');
    return res.json();
  },

  async createGroup(name, creatorId, token) {
    const res = await fetch(`${API_URL}/groups/create`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}` 
      },
      body: JSON.stringify({ name, creator_id: creatorId }),
    });
    if (!res.ok) throw new Error('Failed to create group');
    return res.json();
  },

  async getGroupMessages(groupId, token) {
    const res = await fetch(`${API_URL}/groups/${groupId}/messages`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to get group messages');
    return res.json();
  },

  async sendGroupMessage(groupId, senderId, content, token) {
    const res = await fetch(`${API_URL}/groups/message`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}` 
      },
      body: JSON.stringify({ group_id: groupId, sender_id: senderId, content }),
    });
    if (!res.ok) throw new Error('Failed to send group message');
    return res.json();
  },

  async searchUsers(query, token) {
    const res = await fetch(`${API_URL}/auth/search?q=${encodeURIComponent(query)}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to search users');
    return res.json();
  },

  async addGroupMember(groupId, userId, token) {
    const res = await fetch(`${API_URL}/groups/${groupId}/members`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}` 
      },
      body: JSON.stringify({ user_id: userId }),
    });
    if (!res.ok) throw new Error('Failed to add member');
    return res.json();
  },

  async getGroupMembers(groupId, token) {
    const res = await fetch(`${API_URL}/groups/${groupId}/members`, {
      method: 'GET',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to get members');
    return res.json();
  },

  async getConversations(userId, token) {
    const res = await fetch(`${API_URL}/dm/conversations/${userId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to get conversations');
    return res.json();
  },

  async getGlobalChat(token) {
    const res = await fetch(`${API_URL}/global/messages`, {
      method: 'GET',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to get global messages');
    return res.json();
  },

  async sendGlobalMessage(senderId, content, token) {
    const res = await fetch(`${API_URL}/global/message`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}` 
      },
      body: JSON.stringify({ sender_id: senderId, content }),
    });
    if (!res.ok) throw new Error('Failed to send global message');
    return res.json();
  },
};