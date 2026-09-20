const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "/api";

export type DatasetDataType = string;

export interface ColumnSchema {
  name: string;
  data_type: DatasetDataType;
  nullable: boolean;
  sample_values: string[];
}

export interface TableSchema {
  name: string;
  row_count: number;
  columns: ColumnSchema[];
}

export interface DatasetResponse {
  dataset_id: string;
  dataset_name: string;
  table_names: string[];
  tables: TableSchema[];
}

export interface QueryResult {
  columns: string[];
  rows: unknown[][];
}

export interface QueryExecutionMetadata {
  query_id: string;
  selected_tables: string[];
  rows_returned: number;
  agent_1_duration_ms: number;
  agent_2_duration_ms: number;
  sql_validation_duration_ms: number;
  database_execution_duration_ms: number;
  total_duration_ms: number;
}

export interface QueryExecutionResponse {
  question: string;
  selected_tables: string[];
  sql: string;
  explanation: string;
  result: QueryResult;
  metadata: QueryExecutionMetadata;
}

export async function loadDataset(
  filePath: string,
  tableName: string,
  datasetName: string,
): Promise<DatasetResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/datasets`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        file_path: filePath,
        table_name: tableName,
        dataset_name: datasetName,
      }),
    },
  );

  if (!response.ok) {
    const error = await response.json().catch(() => null);

    throw new Error(
      error?.detail ?? "Failed to load dataset.",
    );
  }

  return response.json();
}

export async function executeQuery(
  question: string,
  datasetId: string,
): Promise<QueryExecutionResponse> {
  const response = await fetch(
    `${API_BASE_URL}/api/query`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question,
        dataset_id: datasetId,
      }),
    },
  );

  if (!response.ok) {
    const error = await response.json().catch(() => null);

    throw new Error(
      error?.detail ?? "Query execution failed.",
    );
  }

  return response.json();
}

export async function checkHealth(): Promise<{
  status: string;
  service: string;
}> {
  const response = await fetch(
    `${API_BASE_URL}/health`,
  );

  if (!response.ok) {
    throw new Error("Backend is unavailable.");
  }

  return response.json();
}

export async function uploadDataset(
  file: File,
): Promise<DatasetResponse> {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/api/datasets/upload`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    const error = await response.json().catch(() => null);

    throw new Error(
      error?.detail ?? "Dataset upload failed.",
    );
  }

  return response.json();
}