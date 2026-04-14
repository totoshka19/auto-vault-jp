'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { Carousel } from '@mantine/carousel';
import {
  Container,
  Grid,
  Image,
  Title,
  Text,
  Badge,
  Group,
  Stack,
  Paper,
  Table,
  Button,
  Skeleton,
  Alert,
  Anchor,
} from '@mantine/core';
import api from '@/lib/axios';
import { useAuthStore } from '@/lib/store';
import { yenToRub, formatRub } from '@/lib/currency';
import type { Car } from '@/lib/types';

function formatMileage(km: number) {
  return `${km.toLocaleString('ru-RU')} км`;
}

const SPEC_LABELS: Partial<Record<keyof Car, string>> = {
  year: 'Год выпуска',
  mileage: 'Пробег',
  transmission: 'Трансмиссия',
  body_type: 'Тип кузова',
  engine_volume: 'Объём двигателя',
  fuel_type: 'Тип топлива',
  drive_type: 'Привод',
  color: 'Цвет',
  has_accidents: 'История ремонтов',
};

function formatValue(key: keyof Car, value: unknown): string {
  if (key === 'has_accidents') {
    if (value === true) return 'Есть';
    if (value === false) return 'Нет';
    return 'Нет данных';
  }
  if (value == null) return '—';
  if (key === 'mileage') return formatMileage(value as number);
  if (key === 'year') return `${value} г.`;
  return String(value);
}

export default function CarDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const token = useAuthStore((s) => s.token);
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); }, []);

  const { data: car, isLoading, isError } = useQuery<Car>({
    queryKey: ['car', id],
    queryFn: async () => {
      const { data } = await api.get<Car>(`/cars/${id}`);
      return data;
    },
    enabled: mounted && !!token && !!id,
  });

  if (!mounted) return null;

  const photos = car?.photos?.length ? car.photos : [];
  const title = `${car?.brand ?? ''} ${car?.model ?? ''}`.trim() || 'Автомобиль';

  return (
    <Container size="lg" py="lg">
      <Button variant="subtle" mb="md" onClick={() => router.back()}>
        ← Назад
      </Button>

      {isError && (
        <Alert color="red">Не удалось загрузить данные автомобиля.</Alert>
      )}

      {isLoading ? (
        <Stack>
          <Skeleton height={400} radius="md" />
          <Skeleton height={40} width="60%" />
          <Skeleton height={200} />
        </Stack>
      ) : car ? (
        <Grid gap="xl">
          {/* Левая колонка — фото */}
          <Grid.Col span={{ base: 12, md: 7 }}>
            {photos.length > 0 ? (
              <Carousel
                emblaOptions={{ loop: true }}
                height={380}
                styles={{ indicator: { background: 'var(--mantine-color-blue-6)' } }}
              >
                {photos.map((src, i) => (
                  <Carousel.Slide key={i}>
                    <Image
                      src={src}
                      height={380}
                      fit="cover"
                      radius="md"
                      alt={`${title} фото ${i + 1}`}
                      fallbackSrc="https://placehold.co/800x380/e9ecef/868e96?text=No+Photo"
                    />
                  </Carousel.Slide>
                ))}
              </Carousel>
            ) : (
              <Image
                src={null}
                height={380}
                radius="md"
                alt={title}
                fallbackSrc="https://placehold.co/800x380/e9ecef/868e96?text=No+Photo"
              />
            )}
          </Grid.Col>

          {/* Правая колонка — основная инфо */}
          <Grid.Col span={{ base: 12, md: 5 }}>
            <Stack gap="md">
              <Title order={2}>{title}</Title>

              <Text fw={700} size="xl" c="blue">
                {car.price != null ? formatRub(yenToRub(car.price)) : '—'}
              </Text>

              <Group gap="xs" wrap="wrap">
                {car.transmission && (
                  <Badge variant="light">{car.transmission}</Badge>
                )}
                {car.fuel_type && (
                  <Badge variant="light" color="teal">{car.fuel_type}</Badge>
                )}
                {car.body_type && (
                  <Badge variant="light" color="violet">{car.body_type}</Badge>
                )}
                {car.drive_type && (
                  <Badge variant="light" color="orange">{car.drive_type}</Badge>
                )}
                {car.has_accidents === false && (
                  <Badge variant="light" color="green">Без ремонтов</Badge>
                )}
                {car.has_accidents === true && (
                  <Badge variant="light" color="red">Были ремонты</Badge>
                )}
              </Group>

              <Group gap="xl">
                <Stack gap={2}>
                  <Text size="xs" c="dimmed">Год</Text>
                  <Text fw={600}>{car.year ?? '—'}</Text>
                </Stack>
                <Stack gap={2}>
                  <Text size="xs" c="dimmed">Пробег</Text>
                  <Text fw={600}>{car.mileage != null ? formatMileage(car.mileage) : '—'}</Text>
                </Stack>
                <Stack gap={2}>
                  <Text size="xs" c="dimmed">Двигатель</Text>
                  <Text fw={600}>{car.engine_volume ?? '—'}</Text>
                </Stack>
              </Group>

              {car.url && (
                <Anchor href={car.url} target="_blank" size="sm" c="dimmed">
                  Оригинал на CarSensor.net →
                </Anchor>
              )}
            </Stack>
          </Grid.Col>

          {/* Полная таблица характеристик */}
          <Grid.Col span={12}>
            <Paper withBorder p="md" radius="md">
              <Title order={4} mb="md">Характеристики</Title>
              <Table>
                <Table.Tbody>
                  {(Object.keys(SPEC_LABELS) as Array<keyof Car>).map((key) => (
                    <Table.Tr key={key}>
                      <Table.Td w="40%" c="dimmed">{SPEC_LABELS[key]}</Table.Td>
                      <Table.Td fw={500}>{formatValue(key, car[key])}</Table.Td>
                    </Table.Tr>
                  ))}
                  {car.price != null && (
                    <Table.Tr>
                      <Table.Td c="dimmed">Цена</Table.Td>
                      <Table.Td fw={600} c="blue">{formatRub(yenToRub(car.price))}</Table.Td>
                    </Table.Tr>
                  )}
                </Table.Tbody>
              </Table>
            </Paper>
          </Grid.Col>
        </Grid>
      ) : null}
    </Container>
  );
}
