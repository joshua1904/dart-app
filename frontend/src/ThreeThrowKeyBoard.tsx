import {Component} from "preact";
import register from "preact-custom-element";

interface Props {

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

}
export class ThreeThrowKeyBoard extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        console.log("ThreeThrowKeyBoard constructor");
        this.state = { [Focus.H1]: "", [Focus.H2]: "", [Focus.H3]: "", focus: Focus.H1, type: HitType.S};
    }

    setType = (t: HitType) => {
        this.setState({ type: t });
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
        const current_focus = this.state.focus;
        if(this.state[current_focus] == "") {
            this.moveFocusPrev()
            const new_focus = current_focus > 0 ? current_focus - 1 : current_focus
            this.setState({[new_focus]: ""})


        }
        this.setState({[current_focus]: "" } )

    }
    get_pointsFromPointString = (pointString: string | null) => {
        if (!pointString){
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
        console.log(points)
        points += this.get_pointsFromPointString(this.state[Focus.H2]);
                console.log(points)
        points += this.get_pointsFromPointString(this.state[Focus.H3]);
        console.log(points);
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
        this.setState({[this.state.focus]: showValue})
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
            <div class="mb-3">
                <div class="input-group input-group-lg">
                    <div class="form-control form-control-lg text-center"
                         aria-readonly="true"
                         tabIndex={-1}
                         style="font-size: 1.5rem; font-weight: bold; user-select: none; pointer-events: none;">
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
                             style="font-size: 1.5rem; font-weight: bold; user-select: none; pointer-events: none;">
                            {this.state[Focus.H1] || '\u00A0'}
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="form-control form-control-lg text-center"
                             aria-readonly="true"
                             tabIndex={-1}
                             style="font-size: 1.5rem; font-weight: bold; user-select: none; pointer-events: none;">
                            {this.state[Focus.H2] || '\u00A0'}
                        </div>
                    </div>
                    <div class="col-4">
                        <div class="form-control form-control-lg text-center"
                             aria-readonly="true"
                             tabIndex={-1}
                             style="font-size: 1.5rem; font-weight: bold; user-select: none; pointer-events: none;">
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
                        for (let i = 0; i < values.length; i += 4) {
                            const slice = values.slice(i, i + 4);
                            rows.push(
                                <div class="row g-2 justify-content-center mb-2" key={`row-${i}`}>
                                    {slice.map(v => {
                                        const isDisabled = this.is_disabled(v);
                                        const btnClass = `btn btn-lg ${isDisabled ? 'btn-secondary' : 'btn-outline-secondary'}`;
                                        return (
                                            <div class="col-3 d-grid" key={`num-${v}`}>
                                                <button type="button" class={btnClass} style="font-size: 1.05rem;" onClick={() => this.handleSelect(v)} disabled={isDisabled}>{v}</button>
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