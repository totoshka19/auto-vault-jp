'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  TextInput,
  PasswordInput,
  Button,
  Paper,
  Title,
  Text,
  Stack,
  Center,
  Alert,
} from '@mantine/core';
import { useForm } from '@mantine/form';
import api from '@/lib/axios';
import { useAuthStore } from '@/lib/store';

export default function LoginPage() {
  const router = useRouter();
  const setToken = useAuthStore((s) => s.setToken);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const form = useForm({
    initialValues: { username: '', password: '' },
    validate: {
      username: (v) => (v.trim() ? null : 'Введите логин'),
      password: (v) => (v.trim() ? null : 'Введите пароль'),
    },
  });

  const handleSubmit = async (values: typeof form.values) => {
    setError(null);
    setLoading(true);
    try {
      const { data } = await api.post<{ access_token: string }>('/auth/login', values);
      setToken(data.access_token);
      localStorage.setItem('token', data.access_token);
      router.push('/');
    } catch {
      setError('Неверный логин или пароль');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Center h="100vh">
      <Paper w={360} p="xl" radius="md" withBorder>
        <Title order={2} mb="xs" ta="center">
          AutoVault JP
        </Title>
        <Text c="dimmed" size="sm" ta="center" mb="lg">
          Войдите, чтобы продолжить
        </Text>

        {error && (
          <Alert color="red" mb="md" radius="md">
            {error}
          </Alert>
        )}

        <form onSubmit={form.onSubmit(handleSubmit)}>
          <Stack gap="sm">
            <TextInput
              label="Логин"
              placeholder="admin"
              {...form.getInputProps('username')}
            />
            <PasswordInput
              label="Пароль"
              placeholder="••••••••"
              {...form.getInputProps('password')}
            />
            <Button type="submit" fullWidth mt="sm" loading={loading}>
              Войти
            </Button>
          </Stack>
        </form>
      </Paper>
    </Center>
  );
}
