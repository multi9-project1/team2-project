import React, { useMemo, useState } from "react";

export default function ApiRecommendTest() {
  const [apiBaseUrl, setApiBaseUrl] = useState("http://localhost:8000");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [responseData, setResponseData] = useState(null);

  const [form, setForm] = useState({
    gender: "W",
    personal_color_input: "unknown",
    warmcool_q1: "B",
    warmcool_q2: "B",
    warmcool_q3: "B",
    qwarm: "A",
    qcool: "D",
    qstyle_1: "B",
    qstyle_2: "B",
    qstyle_3: "B",
    qstyle_4: "A",
    qstyle_5: "B",
    qstyle_6: "A",
    top_k: 5,
    strategy: "hybrid",
    target_style: "",
  });

  const requestBody = useMemo(() => {
    return {
      ...form,
      target_style: form.target_style?.trim() || null,
    };
  }, [form]);

  const handleChange = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const sendRequest = async () => {
    setLoading(true);
    setError("");
    setResponseData(null);

    try {
      const res = await fetch(`${apiBaseUrl}/api/recommend`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data?.detail || "API 호출에 실패했습니다.");
      }

      setResponseData(data);
    } catch (err) {
      setError(err.message || "알 수 없는 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  const testHealth = async () => {
    setLoading(true);
    setError("");
    setResponseData(null);

    try {
      const res = await fetch(`${apiBaseUrl}/health`);
      const data = await res.json();

      if (!res.ok) {
        throw new Error("헬스체크 실패");
      }

      setResponseData(data);
    } catch (err) {
      setError(err.message || "헬스체크 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-6xl space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">FastAPI 추천 API 테스트</h1>
          <p className="mt-2 text-sm text-slate-600">
            FastAPI 서버가 켜져 있으면 이 화면에서 바로 추천 호출이 됩니다.
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
            <h2 className="mb-4 text-lg font-semibold text-slate-900">API 설정 / 요청값</h2>

            <div className="space-y-4">
              <Field label="API Base URL">
                <input
                  className="w-full rounded-xl border border-slate-300 px-3 py-2 outline-none focus:border-slate-500"
                  value={apiBaseUrl}
                  onChange={(e) => setApiBaseUrl(e.target.value)}
                  placeholder="http://localhost:8000"
                />
              </Field>

              <div className="grid grid-cols-2 gap-3">
                <Field label="gender">
                  <select
                    className="w-full rounded-xl border border-slate-300 px-3 py-2"
                    value={form.gender}
                    onChange={(e) => handleChange("gender", e.target.value)}
                  >
                    <option value="W">W</option>
                    <option value="M">M</option>
                  </select>
                </Field>

                <Field label="personal_color_input">
                  <select
                    className="w-full rounded-xl border border-slate-300 px-3 py-2"
                    value={form.personal_color_input}
                    onChange={(e) => handleChange("personal_color_input", e.target.value)}
                  >
                    <option value="unknown">unknown</option>
                    <option value="spring_light">spring_light</option>
                    <option value="spring_bright">spring_bright</option>
                    <option value="autumn_muted">autumn_muted</option>
                    <option value="autumn_deep">autumn_deep</option>
                    <option value="summer_light">summer_light</option>
                    <option value="summer_muted">summer_muted</option>
                    <option value="winter_bright">winter_bright</option>
                    <option value="winter_deep">winter_deep</option>
                    <option value="spring_warm">spring_warm</option>
                    <option value="summer_cool">summer_cool</option>
                    <option value="autumn_warm">autumn_warm</option>
                    <option value="winter_cool">winter_cool</option>
                  </select>
                </Field>
              </div>

              <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
                <SelectField label="warmcool_q1" value={form.warmcool_q1} onChange={(v) => handleChange("warmcool_q1", v)} options={["A", "B"]} />
                <SelectField label="warmcool_q2" value={form.warmcool_q2} onChange={(v) => handleChange("warmcool_q2", v)} options={["A", "B"]} />
                <SelectField label="warmcool_q3" value={form.warmcool_q3} onChange={(v) => handleChange("warmcool_q3", v)} options={["A", "B"]} />
                <SelectField label="qwarm" value={form.qwarm} onChange={(v) => handleChange("qwarm", v)} options={["A", "B", "C", "D"]} />
                <SelectField label="qcool" value={form.qcool} onChange={(v) => handleChange("qcool", v)} options={["A", "B", "C", "D"]} />
              </div>

              <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
                <SelectField label="qstyle_1" value={form.qstyle_1} onChange={(v) => handleChange("qstyle_1", v)} options={["A", "B"]} />
                <SelectField label="qstyle_2" value={form.qstyle_2} onChange={(v) => handleChange("qstyle_2", v)} options={["A", "B"]} />
                <SelectField label="qstyle_3" value={form.qstyle_3} onChange={(v) => handleChange("qstyle_3", v)} options={["A", "B"]} />
                <SelectField label="qstyle_4" value={form.qstyle_4} onChange={(v) => handleChange("qstyle_4", v)} options={["A", "B"]} />
                <SelectField label="qstyle_5" value={form.qstyle_5} onChange={(v) => handleChange("qstyle_5", v)} options={["A", "B"]} />
                <SelectField label="qstyle_6" value={form.qstyle_6} onChange={(v) => handleChange("qstyle_6", v)} options={["A", "B"]} />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <Field label="top_k">
                  <input
                    type="number"
                    min={1}
                    max={30}
                    className="w-full rounded-xl border border-slate-300 px-3 py-2"
                    value={form.top_k}
                    onChange={(e) => handleChange("top_k", Number(e.target.value))}
                  />
                </Field>

                <Field label="strategy">
                  <select
                    className="w-full rounded-xl border border-slate-300 px-3 py-2"
                    value={form.strategy}
                    onChange={(e) => handleChange("strategy", e.target.value)}
                  >
                    <option value="hybrid">hybrid</option>
                    <option value="cosine">cosine</option>
                    <option value="mapped">mapped</option>
                  </select>
                </Field>
              </div>

              <Field label="target_style (optional)">
                <input
                  className="w-full rounded-xl border border-slate-300 px-3 py-2"
                  value={form.target_style}
                  onChange={(e) => handleChange("target_style", e.target.value)}
                  placeholder="예: retro"
                />
              </Field>

              <div className="flex flex-wrap gap-3 pt-2">
                <button
                  onClick={testHealth}
                  disabled={loading}
                  className="rounded-2xl bg-slate-200 px-4 py-2 text-sm font-medium text-slate-800 transition hover:bg-slate-300 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loading ? "요청 중..." : "Health 확인"}
                </button>
                <button
                  onClick={sendRequest}
                  disabled={loading}
                  className="rounded-2xl bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loading ? "요청 중..." : "추천 호출"}
                </button>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
              <h2 className="mb-3 text-lg font-semibold text-slate-900">요청 JSON</h2>
              <pre className="overflow-auto rounded-xl bg-slate-950 p-4 text-xs text-slate-100">
                {JSON.stringify(requestBody, null, 2)}
              </pre>
            </div>

            <div className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
              <h2 className="mb-3 text-lg font-semibold text-slate-900">응답 / 에러</h2>
              {error ? (
                <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {error}
                </div>
              ) : responseData ? (
                <pre className="overflow-auto rounded-xl bg-slate-950 p-4 text-xs text-slate-100">
                  {JSON.stringify(responseData, null, 2)}
                </pre>
              ) : (
                <div className="rounded-xl border border-dashed border-slate-300 px-4 py-8 text-sm text-slate-500">
                  아직 응답이 없습니다.
                </div>
              )}
            </div>
          </div>
        </div>

        {Array.isArray(responseData?.items) && responseData.items.length > 0 && (
          <div className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-slate-200">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900">추천 결과</h2>
              <span className="text-sm text-slate-500">{responseData.items.length} items</span>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {responseData.items.map((item) => (
                <div key={item.item_id} className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
                  <div className="aspect-[4/5] bg-slate-100">
                    {item.image_url ? (
                      <img
                        src={item.image_url}
                        alt={item.name || item.item_id}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <div className="flex h-full items-center justify-center text-sm text-slate-400">
                        이미지 없음
                      </div>
                    )}
                  </div>

                  <div className="space-y-2 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-sm text-slate-500">{item.mall || "unknown mall"}</p>
                        <h3 className="line-clamp-2 text-sm font-semibold text-slate-900">
                          {item.name || item.item_id}
                        </h3>
                      </div>
                      <span className="rounded-full bg-slate-100 px-2 py-1 text-xs font-medium text-slate-700">
                        {typeof item.score === "number" ? item.score.toFixed(3) : "-"}
                      </span>
                    </div>

                    {item.brand && <p className="text-sm text-slate-600">브랜드: {item.brand}</p>}
                    {item.style && <p className="text-sm text-slate-600">스타일: {item.style}</p>}

                    {Array.isArray(item.reason) && item.reason.length > 0 && (
                      <ul className="list-disc space-y-1 pl-5 text-xs text-slate-500">
                        {item.reason.map((reason, idx) => (
                          <li key={idx}>{reason}</li>
                        ))}
                      </ul>
                    )}

                    <div className="flex flex-wrap gap-2 pt-2">
                      {item.deep_link && (
                        <a
                          href={item.deep_link}
                          target="_blank"
                          rel="noreferrer"
                          className="rounded-xl bg-slate-900 px-3 py-2 text-xs font-medium text-white"
                        >
                          딥링크 이동
                        </a>
                      )}
                      {item.web_url && (
                        <a
                          href={item.web_url}
                          target="_blank"
                          rel="noreferrer"
                          className="rounded-xl bg-slate-200 px-3 py-2 text-xs font-medium text-slate-800"
                        >
                          웹 링크
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <label className="block space-y-1">
      <span className="text-sm font-medium text-slate-700">{label}</span>
      {children}
    </label>
  );
}

function SelectField({ label, value, onChange, options }) {
  return (
    <Field label={label}>
      <select
        className="w-full rounded-xl border border-slate-300 px-3 py-2"
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </Field>
  );
}
