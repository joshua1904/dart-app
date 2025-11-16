import {Component} from "preact";
import register from "preact-custom-element";

interface Props {
    setPoints: (points: number, throwsLeft: number) => void;
}
enum HitType {
    S = 0,
    D = 1,
    T = 2,
}
enum Focus {
    H1= 0,
    H2 = 1,
    H3 = 2,
}

interface State {
    [Focus.H1]: string;
    [Focus.H2]: string;
    [Focus.H3]: string;
    focus: Focus;
    type: HitType;
    ended_with_double: boolean;
}
export class ThreeThrowKeyBoard extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { [Focus.H1]: "", [Focus.H2]: "", [Focus.H3]: "", focus: Focus.H1, type: HitType.S, ended_with_double: false};
    }

    setType = (t: HitType) => {
        if (this.state["type"]) {
            this.setState({type: HitType.S})
        }
        else {
            this.setState({ type: t });
        }

    }


    setEndedWithDouble = () => {
        const throwsList = [this.state[Focus.H1], this.state[Focus.H2], this.state[Focus.H3]];
        const lastNonEmpty = [...throwsList].reverse().find(v => v && v.length > 0) || "";
        const ended = lastNonEmpty.startsWith("D") || lastNonEmpty === "BULL";
        if (ended !== this.state.ended_with_double) {
            this.setState({ ended_with_double: ended });
        }
    }
    componentDidUpdate(prevProps: Props, prevState: State) {
        if (
            prevState[Focus.H1] !== this.state[Focus.H1] ||
            prevState[Focus.H2] !== this.state[Focus.H2] ||
            prevState[Focus.H3] !== this.state[Focus.H3]
        ) {
            this.setEndedWithDouble();
            // no-op here; we notify via setState callbacks to guarantee fresh values
        }
    }
         throws_left = () => {
             let left_throws = 3
             if (this.state[Focus.H1]) {
                 left_throws--
             }
             if (this.state[Focus.H2]) {
                 left_throws--
             }
             if (this.state[Focus.H3]) {
                 left_throws--
             }
             return left_throws;
         }


    private moveFocusNext = () => {
        if (this.state.focus === Focus.H1) this.setState({ focus: Focus.H2 });
        else if (this.state.focus === Focus.H2) this.setState({ focus: Focus.H3 });
    }

    private moveFocusPrev = () => {
        if (this.state.focus === Focus.H3) this.setState({ focus: Focus.H2 });
        else if (this.state.focus === Focus.H2) this.setState({ focus: Focus.H1 });
    }


    handleBackspace = () => {
        const currentFocus = this.state.focus;
        const isCurrentEmpty = (this.state[currentFocus] || "") === "";
        if (isCurrentEmpty) {
            const prevFocus = currentFocus === Focus.H3 ? Focus.H2 : (currentFocus === Focus.H2 ? Focus.H1 : Focus.H1);
            this.setState({ focus: prevFocus, [prevFocus]: "" }, () => {
                this.props.setPoints(this.get_pointsFromState(), this.throws_left());
            });
        } else {
            this.setState({ [currentFocus]: "" }, () => {
                this.props.setPoints(this.get_pointsFromState(), this.throws_left());
            });
        }

    }
    get_pointsFromPointString = (pointString: string | null) => {
        if (!pointString || pointString == "Miss"){
            return 0;
        }
        if(pointString == "BULL"){
            return 50;
        }
        let prefix = pointString.substring(0, 1);
        let intValue = parseInt(pointString.substring(1));
        if(prefix == "D"){
            return intValue * 2;
        }
        if(prefix == "T"){
            return intValue * 3;
        }
        return intValue;
        
    }

    get_pointsFromState = () => {
        let points = 0;
        points += this.get_pointsFromPointString(this.state[Focus.H1]);
        points += this.get_pointsFromPointString(this.state[Focus.H2]);
        points += this.get_pointsFromPointString(this.state[Focus.H3]);
        return points;
    }

    handleSelect = (value: number) => {
        let showValue: string = String(value);
        if (value == 0){
           showValue = "Miss"
        }
        else if(this.state.type == HitType.S){
            showValue = "S " + showValue;
        }
        else if (this.state.type == HitType.D){
            showValue = "D " + showValue;
        }
        else if (this.state.type == HitType.T){
            showValue = "T " + showValue;
        }
        if(showValue == "D 25") {
            showValue = "BULL";
        }
        this.setState({[this.state.focus]: showValue}, () => {
            this.props.setPoints(this.get_pointsFromState(), this.throws_left());
        })
        this.setState({type: HitType.S})
        this.moveFocusNext()






    }

    is_disabled = (value: number) => {
        if (value == 0 && this.state.type != HitType.S){
            return true;
        }
        if (value == 25 && this.state.type == HitType.T){
            return true;
        }
        return false;


    }
    render() {
        return <div>
            <input type="hidden" name={"points"} value={this.get_pointsFromState()}/>
            <input type="hidden" name="h1" value={this.state[Focus.H1]} />
            <input type="hidden" name="h2" value={this.state[Focus.H2]} />
            <input type="hidden" name="h3" value={this.state[Focus.H3]} />

            <input type="hidden" name="ended_with_double" value={this.state.ended_with_double ? "true" : "false"} />
            <div class="mb-3">
                <div class="input-group input-group-lg">
                    <div class="form-control form-control-lg text-center"
                         aria-readonly="true"
                         tabIndex={-1}
                         style="font-size: 1.0rem; font-weight: bold; user-select: none; pointer-events: none;">
                        {(this.get_pointsFromState() || '0')}
                    </div>

                    <button type="submit" class="btn btn-primary px-4">
                        <i class="bi bi-check-circle me-2"></i>
                    </button>
                </div>
                <div class="row g-2 mt-2">
                    <div class="col-4">
                        <div class="form-control form-control-lg text-center"
                             aria-readonly="true"
                             tabIndex={-1}
                             style="font-size: 1.0rem; font-weight: bold; user-select: none; pointer-events: none;">
                            {this.state[Focus.H1] || '\u00A0'}
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="form-control form-control-lg text-center"
                             aria-readonly="true"
                             tabIndex={-1}
                             style="font-size: 1.0rem; font-weight: bold; user-select: none; pointer-events: none;">
                            {this.state[Focus.H2] || '\u00A0'}
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="form-control form-control-lg text-center"
                             aria-readonly="true"
                             tabIndex={-1}
                             style="font-size: 1.0rem; font-weight: bold; user-select: none; pointer-events: none;">
                            {this.state[Focus.H3] || '\u00A0'}
                        </div>
                    </div>
                </div>
            </div>
            <div class="mt-3" aria-label="Numeric keypad">
                <div class="row g-2 justify-content-center mb-2">
                    <div class="col-4 d-grid">
                        <button type="button" class="btn btn-outline-dark btn-lg {this.state.type === HitType.D ? 'active' : ''}" onClick={() => this.setType(HitType.D)}>D</button>
                    </div>
                    <div class="col-4 d-grid">
                        <button type="button" class="btn btn-outline-dark btn-lg {this.state.type === HitType.T ? 'active' : ''}" onClick={() => this.setType(HitType.T)}>T</button>
                    </div>
                    <div class="col-4 d-grid">
                        <button type="button" class="btn btn-outline-danger btn-lg" onClick={this.handleBackspace} aria-label="Backspace">
                            <i class="bi bi-backspace me-1"></i>
                        </button>
                    </div>
                </div>
                {
                    (() => {
                        const values = Array.from({ length: 20 }, (_, i) => i + 1).concat([25, 0]);
                        const rows: any[] = [];
                        for (let i = 0; i < values.length; i += 5) {
                            const slice = values.slice(i, i + 5);
                            const isLastRow = i + 5 >= values.length;
                            rows.push(
                                <div class={`row row-cols-5 g-2 mb-2 ${isLastRow ? 'justify-content-center' : ''}`} key={`row-${i}`}>
                                    {slice.map(v => {
                                        const isDisabled = this.is_disabled(v);
                                        const btnClass = `btn btn-lg d-flex justify-content-center align-items-center ${isDisabled ? 'btn-secondary' : 'btn-outline-secondary'}`;
                                        return (
                                            <div class="col d-grid" key={`num-${v}`}>
                                                <button type="button" class={btnClass} style="font-size: 1rem;" onClick={() => this.handleSelect(v)} disabled={isDisabled}>
                                                    <span style="display: inline-block;">{v}</span>
                                                </button>
                                            </div>
                                        );
                                    })}
                                </div>
                            );
                        }
                        return rows;
                    })()
                }
            </div>
        </div>
    }
}
register(ThreeThrowKeyBoard, 'three-throw-keyboard', [], { shadow: false })