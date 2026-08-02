/**
 * PerformanceMonitor
 * Measures real-time FPS and automatically degrades visual effects if frame rate drops below 45 FPS.
 */

type PerformanceLevel = 'high' | 'medium' | 'low';
type Listener = (level: PerformanceLevel) => void;

class PerformanceMonitorManager {
  private frameCount = 0;
  private lastTime = performance.now();
  private fps = 60;
  private level: PerformanceLevel = 'high';
  private listeners: Set<Listener> = new Set();
  private animId: number | null = null;
  private lowFpsCount = 0;

  constructor() {
    if (typeof window !== 'undefined') {
      this.start();
    }
  }

  private start() {
    const loop = () => {
      this.frameCount++;
      const now = performance.now();
      const delta = now - this.lastTime;

      if (delta >= 1000) {
        this.fps = Math.round((this.frameCount * 1000) / delta);
        this.frameCount = 0;
        this.lastTime = now;
        this.evaluate();
      }

      this.animId = requestAnimationFrame(loop);
    };

    this.animId = requestAnimationFrame(loop);
  }

  private evaluate() {
    let nextLevel: PerformanceLevel = this.level;

    if (this.fps < 35) {
      this.lowFpsCount++;
      if (this.lowFpsCount >= 2) {
        nextLevel = 'low';
      }
    } else if (this.fps < 48) {
      this.lowFpsCount++;
      if (this.lowFpsCount >= 2) {
        nextLevel = 'medium';
      }
    } else {
      this.lowFpsCount = Math.max(0, this.lowFpsCount - 1);
      if (this.lowFpsCount === 0 && this.fps >= 55) {
        nextLevel = 'high';
      }
    }

    if (nextLevel !== this.level) {
      this.level = nextLevel;
      this.listeners.forEach((fn) => fn(this.level));
    }
  }

  public subscribe(listener: Listener): () => void {
    this.listeners.add(listener);
    listener(this.level);
    return () => this.listeners.delete(listener);
  }

  public getLevel(): PerformanceLevel {
    return this.level;
  }

  public getFps(): number {
    return this.fps;
  }
}

export const performanceMonitor = new PerformanceMonitorManager();
