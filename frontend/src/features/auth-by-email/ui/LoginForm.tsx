import React, { useState } from 'react';
import { useUserStore } from '@/entities/user';

export const LoginForm: React.FC = () => {
  const { setUser } = useUserStore();
  const [email, setEmail] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setUser({ id: '1', email });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <button type="submit">Login</button>
    </form>
  );
};
