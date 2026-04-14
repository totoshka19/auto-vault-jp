'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import {
  Container,
  Title,
  Group,
  Button,
  TextInput,
  NumberInput,
  Select,
  SimpleGrid,
  Pagination,
  Paper,
  Text,
  Stack,
  Alert,
  Skeleton,
  Center,
} from '@mantine/core';
import api from '@/lib/axios';
import { useAuthStore } from '@/lib/store';
import { rubToYen } from '@/lib/currency';
import CarCard from '@/components/CarCard';
import type { CarsListResponse } from '@/lib/types';

interface Filters {
  brand: string;
  model: string;
  year_from: number | '';
  year_to: number | '';
  price_min: number | '';
  price_max: number | '';
  mileage_min: number | '';
  mileage_max: number | '';
}

const DEFAULT_FILTERS: Filters = {
  brand: '',
  model: '',
  year_from: '',
  year_to: '',
  price_min: '',
  price_max: '',
  mileage_min: '',
  mileage_max: '',
};

async function fetchCars(
  filters: Filters,
  sort: string,
  order: string,
  page: number
): Promise<CarsListResponse> {
  const params = new URLSearchParams();
  if (filters.brand) params.set('brand', filters.brand);
  if (filters.model) params.set('model', filters.model);
  if (filters.year_from !== '') params.set('year_from', String(filters.year_from));
  if (filters.year_to !== '') params.set('year_to', String(filters.year_to));
  if (filters.price_min !== '') params.set('price_min', String(rubToYen(Number(filters.price_min))));
  if (filters.price_max !== '') params.set('price_max', String(rubToYen(Number(filters.price_max))));
  if (filters.mileage_min !== '') params.set('mileage_min', String(filters.mileage_min));
  if (filters.mileage_max !== '') params.set('mileage_max', String(filters.mileage_max));
  params.set('sort', sort);
  params.set('order', order);
  params.set('page', String(page));
  params.set('limit', '20');

  const { data } = await api.get<CarsListResponse>(`/cars?${params}`);
  return data;
}

export default function CatalogPage() {
  const router = useRouter();
  const { token, logout } = useAuthStore();
  const [mounted, setMounted] = useState(false);

  const [draftFilters, setDraftFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [appliedFilters, setAppliedFilters] = useState<Filters>(DEFAULT_FILTERS);
  const [sort, setSort] = useState('price');
  const [order, setOrder] = useState('asc');
  const [page, setPage] = useState(1);

  useEffect(() => { setMounted(true); }, []);

  useEffect(() => {
    if (mounted && !token) router.push('/login');
  }, [mounted, token, router]);

  const { data, isLoading, isError } = useQuery({
    queryKey: ['cars', appliedFilters, sort, order, page],
    queryFn: () => fetchCars(appliedFilters, sort, order, page),
    enabled: mounted && !!token,
  });

  const handleApply = () => {
    setPage(1);
    setAppliedFilters(draftFilters);
  };

  const handleReset = () => {
    setDraftFilters(DEFAULT_FILTERS);
    setAppliedFilters(DEFAULT_FILTERS);
    setPage(1);
  };

  const handleSortChange = (value: string | null, field: 'sort' | 'order') => {
    if (!value) return;
    setPage(1);
    if (field === 'sort') setSort(value);
    else setOrder(value);
  };

  const handleLogout = () => {
    logout();
    localStorage.removeItem('token');
    router.push('/login');
  };

  if (!mounted) return null;

  return (
    <Container size="xl" py="lg">
      {/* Header */}
      <Group justify="space-between" mb="lg">
        <Title order={2}>AutoVault JP</Title>
        <Button variant="subtle" color="gray" onClick={handleLogout}>
          Выйти
        </Button>
      </Group>

      {/* Filters */}
      <Paper withBorder p="md" radius="md" mb="lg">
        <Stack gap="sm">
          <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="sm">
            <TextInput
              label="Марка"
              placeholder="Toyota, Nissan..."
              value={draftFilters.brand}
              onChange={(e) => setDraftFilters((f) => ({ ...f, brand: e.target.value }))}
            />
            <TextInput
              label="Модель"
              placeholder="Land Cruiser..."
              value={draftFilters.model}
              onChange={(e) => setDraftFilters((f) => ({ ...f, model: e.target.value }))}
            />
            <NumberInput
              label="Год от"
              placeholder="2018"
              min={1990}
              max={2025}
              value={draftFilters.year_from}
              onChange={(v) => setDraftFilters((f) => ({ ...f, year_from: v === '' ? '' : Number(v) }))}
            />
            <NumberInput
              label="Год до"
              placeholder="2024"
              min={1990}
              max={2025}
              value={draftFilters.year_to}
              onChange={(v) => setDraftFilters((f) => ({ ...f, year_to: v === '' ? '' : Number(v) }))}
            />
            <NumberInput
              label="Цена от, ₽"
              placeholder="500 000"
              min={0}
              step={100000}
              value={draftFilters.price_min}
              onChange={(v) => setDraftFilters((f) => ({ ...f, price_min: v === '' ? '' : Number(v) }))}
            />
            <NumberInput
              label="Цена до, ₽"
              placeholder="3 000 000"
              min={0}
              step={100000}
              value={draftFilters.price_max}
              onChange={(v) => setDraftFilters((f) => ({ ...f, price_max: v === '' ? '' : Number(v) }))}
            />
            <NumberInput
              label="Пробег от, км"
              placeholder="0"
              min={0}
              step={10000}
              value={draftFilters.mileage_min}
              onChange={(v) => setDraftFilters((f) => ({ ...f, mileage_min: v === '' ? '' : Number(v) }))}
            />
            <NumberInput
              label="Пробег до, км"
              placeholder="100 000"
              min={0}
              step={10000}
              value={draftFilters.mileage_max}
              onChange={(v) => setDraftFilters((f) => ({ ...f, mileage_max: v === '' ? '' : Number(v) }))}
            />
          </SimpleGrid>

          <Group justify="flex-end" gap="sm">
            <Button variant="default" onClick={handleReset}>Сбросить</Button>
            <Button onClick={handleApply}>Применить</Button>
          </Group>
        </Stack>
      </Paper>

      {/* Sort + Results info */}
      <Group justify="space-between" mb="md" wrap="wrap" gap="sm">
        <Text c="dimmed" size="sm">
          {data ? `Найдено: ${data.total} авто` : ''}
        </Text>
        <Group gap="sm">
          <Select
            w={160}
            value={sort}
            onChange={(v) => handleSortChange(v, 'sort')}
            data={[
              { value: 'price', label: 'По цене' },
              { value: 'year', label: 'По году' },
              { value: 'mileage', label: 'По пробегу' },
            ]}
          />
          <Select
            w={160}
            value={order}
            onChange={(v) => handleSortChange(v, 'order')}
            data={[
              { value: 'asc', label: 'По возрастанию' },
              { value: 'desc', label: 'По убыванию' },
            ]}
          />
        </Group>
      </Group>

      {/* Error */}
      {isError && (
        <Alert color="red" mb="md">
          Не удалось загрузить данные. Попробуйте позже.
        </Alert>
      )}

      {/* Cards grid */}
      {isLoading ? (
        <SimpleGrid cols={{ base: 1, sm: 2, md: 3, lg: 4 }} spacing="md">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} height={300} radius="md" />
          ))}
        </SimpleGrid>
      ) : data?.items.length === 0 ? (
        <Center py="xl">
          <Text c="dimmed">Автомобили не найдены</Text>
        </Center>
      ) : (
        <SimpleGrid cols={{ base: 1, sm: 2, md: 3, lg: 4 }} spacing="md">
          {data?.items.map((car) => (
            <CarCard key={car.id} car={car} />
          ))}
        </SimpleGrid>
      )}

      {/* Pagination */}
      {data && data.pages > 1 && (
        <Center mt="xl">
          <Pagination
            total={data.pages}
            value={page}
            onChange={(p) => { setPage(p); window.scrollTo(0, 0); }}
          />
        </Center>
      )}
    </Container>
  );
}
