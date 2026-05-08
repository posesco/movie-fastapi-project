import http from "k6/http";
import { check, sleep } from "k6";
import { Rate } from "k6/metrics";

const errorRate = new Rate("errors");

export const options = {
  stages: [
    { duration: "30s", target: 20 },
    { duration: "1m", target: 20 },
    { duration: "10s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<500"],
    errors: ["rate<0.01"],
  },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
// Categorías válidas: min_length=3, max_length=30
const CATEGORIES = ["Action", "Drama", "Comedy", "Horror", "Thriller"];

export default function () {
  const category = CATEGORIES[Math.floor(Math.random() * CATEGORIES.length)];
  const res = http.get(
    `${BASE_URL}/api/v1/movies/category/?category=${encodeURIComponent(category)}`
  );

  const ok = check(res, {
    "status is 200": (r) => r.status === 200,
    "response is array": (r) => Array.isArray(JSON.parse(r.body)),
    "duration < 500ms": (r) => r.timings.duration < 500,
  });

  errorRate.add(!ok);
  sleep(1);
}
