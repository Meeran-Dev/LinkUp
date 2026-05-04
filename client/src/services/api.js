const API_URL = 'https://linkup-43u1.onrender.com';

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

  async getOnlineUsers(token) {
    const res = await fetch(`${API_URL}/auth/online`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to get online users');
    const data = await res.json();
    return new Set(data.online_users);
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

  async addGroupMember(groupId, userId, creatorId, token) {
    const res = await fetch(`${API_URL}/groups/${groupId}/members?creator_id=${creatorId}`, {
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

  async deleteGroup(groupId, creatorId, token) {
    const res = await fetch(`${API_URL}/groups/${groupId}?creator_id=${creatorId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to delete group');
    return res.json();
  },

  async removeGroupMember(groupId, userId, creatorId, token) {
    const res = await fetch(`${API_URL}/groups/${groupId}/members/${userId}?creator_id=${creatorId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to remove member');
    return res.json();
  },

  getPendingDMs(currentUserId) {
    if (!currentUserId) return [];
    const stored = localStorage.getItem(`pending_dms_${currentUserId}`);
    return stored ? JSON.parse(stored) : [];
  },

  savePendingDM(currentUserId, targetUserId, username) {
    if (!currentUserId || !targetUserId) return;
    const pending = this.getPendingDMs(currentUserId);
    if (!pending.find(p => p.id === targetUserId)) {
      pending.push({ id: targetUserId, username, last_message: '' });
      localStorage.setItem(`pending_dms_${currentUserId}`, JSON.stringify(pending));
    }
  },

  clearPendingDMs(currentUserId) {
    if (!currentUserId) return;
    localStorage.removeItem(`pending_dms_${currentUserId}`);
  },
};