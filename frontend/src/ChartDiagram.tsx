import { Component, createRef } from 'preact';
import register from 'preact-custom-element';

type WeekPoint = { x: string; y: number };

interface Props {
  'week-avg'?: string; // JSON string
}

export class ChartDiagram extends Component<Props> {
  static tagName = 'chart-diagram';
  private canvasRef = createRef<HTMLCanvasElement>();
  private chart: any | null = null;
  private isUnmounted = false;

  componentDidMount() {
    void this.initChart();
  }

  componentWillUnmount() {
    this.isUnmounted = true;
    this.destroyChart();
  }

  private async initChart() {
    const Chart = await this.waitForChart();
    if (this.isUnmounted) return;

    const data = this.parseData(this.props['week-avg']);
    const canvas = this.canvasRef.current;
    if (!canvas || !data) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    this.chart = new Chart(ctx, {
      type: 'line',
      data: {
        datasets: [
          {
            data,
            borderColor: 'rgb(13, 110, 253)',
            backgroundColor: 'rgba(13, 110, 253, 0.15)',
            fill: true,
            tension: 0.35,
            pointRadius: 2,
            pointHoverRadius: 4,
            pointHitRadius: 8,
            borderWidth: 2,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: 'index', intersect: false },
        plugins: {
          legend: { display: false },
          tooltip: {
            mode: 'index',
            intersect: false,
            displayColors: false,
            backgroundColor: 'rgba(0,0,0,0.85)',
            padding: 10,
            titleFont: { weight: '600' },
            bodyFont: { weight: '400' },
          },
        },
        scales: {
          x: {
            type: 'category',
            position: 'bottom',
            labels: data.map((d) => d.x),
            grid: { display: false },
            ticks: { maxRotation: 0, autoSkip: true },
          },
          y: {
            type: 'linear',
            beginAtZero: true,
            grid: { color: 'rgba(0,0,0,0.05)' },
            border: { display: false },
            ticks: { precision: 0 },
          },
        },
      },
    });
  }

  private destroyChart() {
    if (this.chart && typeof this.chart.destroy === 'function') {
      this.chart.destroy();
    }
    this.chart = null;
  }

  private parseData(json?: string): WeekPoint[] | null {
    if (!json) return null;
    try {
      const parsed = JSON.parse(json);
      if (Array.isArray(parsed)) return parsed as WeekPoint[];
      return null;
    } catch {
      return null;
    }
  }

  private waitForChart(): Promise<any> {
    return new Promise((resolve) => {
      const attempt = () => {
        const Chart = (window as any).Chart;
        if (Chart) {
          resolve(Chart);
        } else if (!this.isUnmounted) {
          requestAnimationFrame(attempt);
        }
      };
      attempt();
    });
  }

  render() {
    return (
      <div style="position: relative; width: 100%; max-width: 100%; height: 300px;">
        <canvas ref={this.canvasRef} />
      </div>
    );
  }
}

register(ChartDiagram, 'chart-diagram', ['week-avg'], { shadow: false });


