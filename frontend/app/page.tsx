"use client";

import {
  ChangeEvent,
  FormEvent,
  useState,
} from "react";

import {
  executeQuery,
  uploadDataset,
  DatasetResponse,
  QueryExecutionResponse,
} from "@/lib/api";

export default function Home() {
  const [datasetId, setDatasetId] = useState("");
  const [dataset, setDataset] =
    useState<DatasetResponse | null>(null);
  const [question, setQuestion] = useState(
    "Which country has the highest lifetime customer value?",
  );
  const [result, setResult] =
    useState<QueryExecutionResponse | null>(null);

  const [uploadingDataset, setUploadingDataset] =
    useState(false);
  const [runningQuery, setRunningQuery] =
    useState(false);

  const [error, setError] = useState("");

  async function handleDatasetUpload(
    event: ChangeEvent<HTMLInputElement>,
  ) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    const extension = file.name
      .split(".")
      .pop()
      ?.toLowerCase();

    if (
      extension !== "csv" &&
      extension !== "parquet"
    ) {
      setError(
        "Only CSV and Parquet files are supported.",
      );

      event.target.value = "";
      return;
    }

    setUploadingDataset(true);
    setError("");
    setResult(null);

    try {
      const dataset = await uploadDataset(file);

      setDataset(dataset);
      setDatasetId(dataset.dataset_id);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Dataset upload failed.",
      );
    } finally {
      setUploadingDataset(false);
      event.target.value = "";
    }
  }

  async function handleQuery(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!datasetId) {
      setError("Connect a dataset before running a query.");
      return;
    }

    if (!question.trim()) {
      setError("Enter a question.");
      return;
    }

    setRunningQuery(true);
    setError("");
    setResult(null);

    try {
      const response = await executeQuery(
        question,
        datasetId,
      );

      setResult(response);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Query execution failed.",
      );
    } finally {
      setRunningQuery(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#09090b] text-zinc-100">
      <header className="border-b border-zinc-800 bg-[#0c0c0f]">
        <div className="flex h-16 items-center justify-between px-6">
          <div>
            <h1 className="text-sm font-semibold tracking-wide">
              Data Intelligence Workspace
            </h1>

            <p className="mt-1 text-xs text-zinc-500">
              Natural-language analytics
            </p>
          </div>

          <div className="flex items-center gap-2">
            <StatusBadge label="Workspace" />
            <StatusBadge label="Production" />
            <StatusBadge label="DuckDB" />
            <StatusBadge
              label={
                uploadingDataset
                  ? "Uploading"
                  : datasetId
                    ? "Connected"
                    : "Disconnected"
              }
              active={Boolean(datasetId)}
            />
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-[1600px] p-6">
        <section className="grid grid-cols-4 gap-3">
          <MetricCard
            label="Rows Returned"
            value={
              result
                ? result.metadata.rows_returned.toLocaleString()
                : "—"
            }
          />

          <MetricCard
            label="Query Duration"
            value={
              result
                ? `${Math.round(
                    result.metadata.total_duration_ms,
                  )} ms`
                : "—"
            }
          />

          <MetricCard
            label="Tables Used"
            value={
              result
                ? String(
                    result.selected_tables.length,
                  )
                : "—"
            }
          />

          <MetricCard
            label="Status"
            value={
              runningQuery
                ? "Running"
                : result
                  ? "Complete"
                  : "Ready"
            }
          />
        </section>

        <section className="mt-4 grid grid-cols-[minmax(0,1fr)_280px] gap-4">
          <div className="space-y-4">
            <section className="rounded-lg border border-zinc-800 bg-[#0c0c0f]">
              <div className="flex items-center justify-between border-b border-zinc-800 px-4 py-3">
                <div>
                  <h2 className="text-sm font-medium">
                    Query Console
                  </h2>

                  <p className="mt-1 text-xs text-zinc-500">
                    Upload a dataset, then ask questions in natural language.
                  </p>
                </div>

                <label className="cursor-pointer rounded-md border border-zinc-700 px-3 py-1.5 text-xs text-zinc-300 transition hover:border-zinc-500 hover:bg-zinc-800">
                  {uploadingDataset
                    ? "Uploading..."
                    : datasetId
                      ? "Upload Another Dataset"
                      : "Upload Dataset"}

                  <input
                    type="file"
                    accept=".csv,.parquet"
                    onChange={handleDatasetUpload}
                    disabled={uploadingDataset}
                    className="hidden"
                  />
                </label>
              </div>

              <form
                onSubmit={handleQuery}
                className="p-4"
              >
                <textarea
                  value={question}
                  onChange={(event) =>
                    setQuestion(event.target.value)
                  }
                  rows={4}
                  placeholder="Ask a question about your data..."
                  className="w-full resize-none rounded-md border border-zinc-800 bg-[#09090b] p-4 text-sm text-zinc-200 outline-none placeholder:text-zinc-600 focus:border-zinc-600"
                />

                <div className="mt-3 flex items-center justify-between">
                  <span className="text-xs text-zinc-600">
                    Agentic NL2SQL · OpenRouter
                  </span>

                  <button
                    type="submit"
                    disabled={runningQuery}
                    className="rounded-md bg-zinc-100 px-4 py-2 text-xs font-medium text-zinc-900 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {runningQuery
                      ? "Running Query..."
                      : "Run Query"}
                  </button>
                </div>
              </form>
            </section>

            {error && (
              <section className="rounded-lg border border-red-900/50 bg-red-950/20 p-4">
                <p className="text-sm text-red-400">
                  {error}
                </p>
              </section>
            )}

            {result && (
              <ResultsWorkspace result={result} />
            )}

            {!result && !error && (
              <section className="rounded-lg border border-dashed border-zinc-800 bg-[#0c0c0f] p-10 text-center">
                <p className="text-sm text-zinc-500">
                  Upload a CSV or Parquet dataset to begin.
                </p>
              </section>
            )}
          </div>

          <SchemaPanel dataset={dataset} />
        </section>
      </div>
    </main>
  );
}

function StatusBadge({
  label,
  active = false,
}: {
  label: string;
  active?: boolean;
}) {
  return (
    <span className="rounded-full border border-zinc-800 bg-zinc-900 px-2.5 py-1 text-[10px] text-zinc-400">
      {active && (
        <span className="mr-1.5 inline-block h-1.5 w-1.5 rounded-full bg-emerald-400" />
      )}
      {label}
    </span>
  );
}

function MetricCard({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border border-zinc-800 bg-[#0c0c0f] p-4">
      <p className="text-[10px] uppercase tracking-wider text-zinc-600">
        {label}
      </p>

      <p className="mt-2 text-lg font-medium text-zinc-200">
        {value}
      </p>
    </div>
  );
}

function SchemaPanel({
  dataset,
}: {
  dataset: DatasetResponse | null;
}) {
  return (
    <aside className="rounded-lg border border-zinc-800 bg-[#0c0c0f]">
      <div className="border-b border-zinc-800 px-4 py-3">
        <h2 className="text-sm font-medium">
          Schema
        </h2>

        <p className="mt-1 text-xs text-zinc-500">
          Available data structures
        </p>
      </div>

      <div className="p-4">
        {dataset ? (
          <div className="space-y-4">
            {dataset.tables.map((table) => (
              <div key={table.name}>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-zinc-300">
                    {table.name}
                  </span>

                  <span className="text-[10px] text-zinc-600">
                    {table.row_count.toLocaleString()} rows
                  </span>
                </div>

                <div className="mt-3 space-y-2 border-l border-zinc-800 pl-3">
                  {table.columns.map((column) => (
                    <div
                      key={column.name}
                      className="flex items-center justify-between gap-3"
                    >
                      <span className="truncate text-xs text-zinc-500">
                        {column.name}
                      </span>

                      <span className="shrink-0 text-[10px] text-zinc-700">
                        {column.data_type}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-zinc-600">
            No dataset connected.
          </p>
        )}
      </div>
    </aside>
  );
}

function ResultsWorkspace({
  result,
}: {
  result: QueryExecutionResponse;
}) {
  return (
    <section className="space-y-4">
      <div className="rounded-lg border border-zinc-800 bg-[#0c0c0f]">
        <div className="border-b border-zinc-800 px-4 py-3">
          <h2 className="text-sm font-medium">
            Results
          </h2>

          <p className="mt-1 text-xs text-zinc-500">
            {result.explanation}
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-zinc-800 bg-zinc-900/40">
              <tr>
                {result.result.columns.map(
                  (column) => (
                    <th
                      key={column}
                      className="px-4 py-3 font-medium text-zinc-500"
                    >
                      {column}
                    </th>
                  ),
                )}
              </tr>
            </thead>

            <tbody>
              {result.result.rows.map(
                (row, rowIndex) => (
                  <tr
                    key={rowIndex}
                    className="border-b border-zinc-900 last:border-0"
                  >
                    {row.map(
                      (value, columnIndex) => (
                        <td
                          key={columnIndex}
                          className="px-4 py-3 text-zinc-300"
                        >
                          {String(value)}
                        </td>
                      ),
                    )}
                  </tr>
                ),
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="rounded-lg border border-zinc-800 bg-[#0c0c0f]">
        <div className="border-b border-zinc-800 px-4 py-3">
          <h2 className="text-sm font-medium">
            Generated SQL
          </h2>
        </div>

        <pre className="overflow-x-auto p-4 text-xs leading-6 text-zinc-400">
          <code>{result.sql}</code>
        </pre>
      </div>

      <div className="grid grid-cols-4 gap-3">
        <MetricCard
          label="Agent 1"
          value={`${Math.round(
            result.metadata.agent_1_duration_ms,
          )} ms`}
        />

        <MetricCard
          label="Agent 2"
          value={`${Math.round(
            result.metadata.agent_2_duration_ms,
          )} ms`}
        />

        <MetricCard
          label="Validation"
          value={`${Math.round(
            result.metadata
              .sql_validation_duration_ms,
          )} ms`}
        />

        <MetricCard
          label="DuckDB"
          value={`${Math.round(
            result.metadata
              .database_execution_duration_ms,
          )} ms`}
        />
      </div>
    </section>
  );
}