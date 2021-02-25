import './App.css';
import { ReactComponent as Loader } from './loading.svg';
import { useEffect, Fragment } from 'react';
import { atom, useRecoilState } from 'recoil';

const ENDPOINT = '';

const State = atom({
  key: 'State',
  default: {
    loading: false,
    error: false,
    selected: null,
    list: [],
    recs: []
  }
});

const UsersListView = (props) =>{
  const [state, setState] = useRecoilState(State);
  console.log(state)
  return (
    <ul className="usersList">
      {props.list.map(user => <li onClick={() => {setState({ ...state, selected: user })}} name={user}>{user}</li>)}
    </ul>
  )
}

const RecommendationsView = (props) => {
  let items = []

  console.log(props.data)

  console.log(Object.values(props.data.name))

  for (let i = 0; i < Object.values(props.data.name).length; i++) {

    items.push(
      <a className="item" href={Object.values(props.data.url)[i]} target="_blank" >
        <span className="img" style={{ background: `url(${Object.values(props.data.img)[i]})`}}></span>
        <h1>{Object.values(props.data.name)[i]}</h1>
        <h3 style={{ 'color': '#e65252' }}>
          {Math.round((Object.values(props.data.prediction)[i] /props.scale)*100)} %
        </h3>
        <p title={Object.values(props.data.description)[i]}>{Object.values(props.data.description)[i]}</p>
        <span>Score: {Object.values(props.data.score)[i]} | {Object.values(props.data.totalReviews)[i]}</span>
      </a>
    )
  }
  console.log(items)

  return (
    <article className="full-bleed hotels">
      {items}
    </article>
  )
}

const App = () => {

  const [state, setState] = useRecoilState(State);

  useEffect(()=>{
    let mounted = true;

    const fetchUsers = async () => {
      console.log("Fetching UsersList...");
      setState({ ...state, loading: true });

      try {
        const response = await fetch(ENDPOINT + '/users')

        const data = await response.json();
        setState({ ...state, loading: false, error: false, list: Object.values(data[0]) });

      } catch (err) {
        console.error(err);
        setState({ ...state, loading: false, error: true });
      }
    }

    const fetchRecommendations = async (user) => {
      console.log("Fetching RecommendationsLists...");
      setState({ ...state, loading: true });

      try {
        const responseCB = await fetch(ENDPOINT + '/contentBased/' + user + '/5')
        const contentBased = await responseCB.json();

        const responseCF = await fetch(ENDPOINT + '/collaborativeFilter/' + user + '/5')
        const collaborativeFilter = await responseCF.json();

        setState({ ...state, loading: false, error: false, recs: [contentBased, collaborativeFilter] });

      } catch (err) {
        console.error(err);
        setState({ ...state, loading: false, error: true });
      }
    }

    if (mounted && state.selected == null) fetchUsers();
    if (mounted && state.selected != null) fetchRecommendations(state.selected)
    return () => mounted = false
  }, [state.selected]);

  return (
    <section className="wrapper">
      <h1 style={{ 'textAlign': 'center', 'fontSize': '50px', 'color': '#373737'}}>
        Trip
        <strong style={{ 'color': '#e65252' }}>Rec</strong>
      </h1>
      {
        !state.loading && state.list.length > 0 && state.selected == null &&
        <Fragment>
          <h1>Users ({state.list.length}) : </h1>
          <UsersListView list={state.list} />
        </Fragment>
      }
      {
        !state.loading && state.selected != null && state.recs.length > 0 &&
        <Fragment>
          <a className="back" onClick={() => { setState({ ...state, selected: null, recs: [] }) }}>&lt; Back</a>
          <h1 style={{ 'textAlign': 'center' }}>
            <strong style={{ 'color': '#e65252' }}>“{state.selected}”</strong> recommendations'</h1>

          <h2 style={{'textAlign': 'center'}}>Content Based recommendations</h2>
          <RecommendationsView data={state.recs[0]} scale={1}/>

          <h2 style={{'textAlign': 'center'}}>Collaborative Filtering recommendations</h2>
          <RecommendationsView data={state.recs[1]} scale={5}/>
        </Fragment>
      }
      { state.loading &&
        <Loader/>
      }
    </section>
  );
}

export default App;
