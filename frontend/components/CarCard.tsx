'use client';

import Link from 'next/link';
import { Card, Image, Text, Badge, Group, Stack } from '@mantine/core';
import type { Car } from '@/lib/types';
import { yenToRub, formatRub } from '@/lib/currency';

function formatMileage(km: number) {
  return km >= 10000
    ? `${(km / 10000).toFixed(1)}万km`
    : `${km.toLocaleString('ru-RU')} км`;
}

export default function CarCard({ car }: { car: Car }) {
  return (
    <Card
      component={Link}
      href={`/cars/${car.id}`}
      shadow="sm"
      padding="md"
      radius="md"
      withBorder
      style={{ textDecoration: 'none', cursor: 'pointer' }}
    >
      <Card.Section>
        <Image
          src={car.photos?.[0] ?? null}
          height={180}
          alt={`${car.brand ?? ''} ${car.model ?? ''}`}
          fallbackSrc="https://placehold.co/400x200/e9ecef/868e96?text=No+Photo"
        />
      </Card.Section>

      <Stack gap="xs" mt="md">
        <Text fw={600} size="md" lineClamp={1}>
          {car.brand} {car.model}
        </Text>

        <Group gap={4} wrap="wrap">
          {car.transmission && (
            <Badge size="xs" variant="light">{car.transmission}</Badge>
          )}
          {car.fuel_type && (
            <Badge size="xs" variant="light" color="teal">{car.fuel_type}</Badge>
          )}
          {car.body_type && (
            <Badge size="xs" variant="light" color="violet">{car.body_type}</Badge>
          )}
        </Group>

        <Group justify="space-between">
          <Text size="sm" c="dimmed">{car.year ?? '—'} г.</Text>
          <Text size="sm" c="dimmed">
            {car.mileage != null ? formatMileage(car.mileage) : '—'}
          </Text>
        </Group>

        <Text fw={700} size="lg" c="blue">
          {car.price != null ? formatRub(yenToRub(car.price)) : '—'}
        </Text>
      </Stack>
    </Card>
  );
}
