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
// IDs válidos según el router: ge=1, le=2000
const MOVIE_IDS = [1, 2, 3, 5, 10, 50, 100];

export default function () {
  const id = MOVIE_IDS[Math.floor(Math.random() * MOVIE_IDS.length)];
  const res = http.get(`${BASE_URL}/api/v1/movies/${id}`);

  const ok = check(res, {
    "status is 200 or 404": (r) => r.status === 200 || r.status === 404,
    "duration < 500ms": (r) => r.timings.duration < 500,
  });

  errorRate.add(!ok);
  sleep(1);
}
