export interface Car {
  id: number;
  brand: string | null;
  model: string | null;
  year: number | null;
  mileage: number | null;
  price: number | null;
  transmission: string | null;
  body_type: string | null;
  engine_volume: string | null;
  fuel_type: string | null;
  drive_type: string | null;
  color: string | null;
  has_accidents: boolean | null;
  photos: string[] | null;
  url: string | null;
  created_at: string;
  updated_at: string;
}

export interface CarsListResponse {
  items: Car[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}
