import {Component} from "preact";
import register from "preact-custom-element";

interface Props {
    points: number;
    setPoints: (points: number, throwsLeft: number) => void;
}
interface State {
}

export class SimpleKeyBoard extends Component<Props, State> {
    static tagName = "simple-keyboard";
    constructor(props: Props) {
        super(props);
    }

    handleDigit = (digit: string) => {
        const current = this.props.points ? String(this.props.points) : '';
        const next = current === '0' ? digit : current + digit;
        const clamped = Math.max(0, Math.min(180, parseInt(next, 10) || 0));
        this.props.setPoints(clamped);
    }
    handleBackspace = () => {
        const current = this.props.points ? String(this.props.points) : '';
        const next = current.slice(0, -1);
        this.props.setPoints(parseInt(next, 10) || 0);
    }
    render() {
        return <div>
            <input type="hidden" name="points" value={this.props.points} />
            <div class="mb-3">
                <div class="input-group input-group-lg">
                    <div class="form-control form-control-lg text-center"
                         aria-readonly="true"
                         tabIndex={-1}
                         style="font-size: 1.5rem; font-weight: bold; user-select: none; pointer-events: none;">
                        {this.props.points ? String(this.props.points) : '0'}
                    </div>

                    <button type="submit" class="btn btn-primary px-4">
                        <i class="bi bi-check-circle me-2"></i>
                    </button>
                </div>
            </div>
            <div class="mt-3" aria-label="Numeric keypad">
                <div class="row g-2 justify-content-center mb-2">
                    <div class="col-4 d-grid">
                        <button type="button" class="btn btn-outline-secondary btn-lg" onClick={() => this.handleDigit('1')}>1</button>
                    </div>
                    <div class="col-4 d-grid">
                        <button type="button" class="btn btn-outline-secondary btn-lg" onClick={() => this.handleDigit('2')}>2</button>
                    </div>
                    <div class="col-4 d-grid">
                        <button type="button" class="btn btn-outline-secondary btn-lg" onClick={() => this.handleDigit('3')}>3</button>
                    </div>
                </div>
                <div class="row g-2 justify-content-center mb-2">
                    <div class="col-4 d-grid">
                        <button type="button" class="btn btn-outline-secondary btn-lg" onClick={() => this.handleDigit('4')}>4</button>
                    </div>
                    <div class="col-4 d-grid">
                        <button type="button" class="btn btn-outline-secondary btn-lg" onClick={() => this.handleDigit('5')}>5</button>
                    </div>
                    <div class="col-4 d-grid">
                        <button type="button" class="btn btn-outline-secondary btn-lg" onClick={() => this.handleDigit('6')}>6</button>
                    </div>
                </div>
                <div class="row g-2 justify-content-center mb-2">
                    <div class="col-4 d-grid">
                        <button type="button" class="btn btn-outline-secondary btn-lg" onClick={() => this.handleDigit('7')}>7</button>
                    </div>
                    <div class="col-4 d-grid">
                        <button type="button" class="btn btn-outline-secondary btn-lg" onClick={() => this.handleDigit('8')}>8</button>
                    </div>
                    <div class="col-4 d-grid">
                        <button type="button" class="btn btn-outline-secondary btn-lg" onClick={() => this.handleDigit('9')}>9</button>
                    </div>
                </div>
                <div class="row g-2 justify-content-center">
                    <div class="col-4 d-grid"></div>
                    <div class="col-4 d-grid">
                        <button type="button" class="btn btn-outline-secondary btn-lg" onClick={() => this.handleDigit('0')}>0</button>
                    </div>
                    <div class="col-4 d-grid">
                        <button type="button" class="btn btn-outline-danger btn-lg" onClick={this.handleBackspace} aria-label="Backspace">
                            <i class="bi bi-backspace me-1"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    }
}
register(SimpleKeyBoard, 'simple-keyboard', [], { shadow: false })